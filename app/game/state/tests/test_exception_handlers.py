from unittest.mock import Mock

import pytest

from app.core.exception_handler_store import ExceptionHandlerStore
from app.core.ioc import IoC
from app.game.setup.state import ioc_setup_game_state
from app.game.state.event_loop import EventLoop
from app.game.state.exception_handlers import (
    FirstRetryCommand,
    LogExceptionCommand,
    SecondRetryCommand,
    delayed_first_retry_handler,
    delayed_log_exception_handler,
    delayed_second_retry_handler,
)
from tests.mocks import MockCommand


class MockError(Exception): ...


@pytest.fixture(autouse=True)
def _ioc_setup() -> None:
    ioc_setup_game_state()


@pytest.fixture()
def exception_handler_store() -> ExceptionHandlerStore:
    return IoC[ExceptionHandlerStore].resolve("ExceptionHandlerStore")


@pytest.fixture()
def event_loop() -> EventLoop:
    return IoC[EventLoop].resolve("EventLoop")


@pytest.fixture()
def mock_log_exception_command(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """
    Создать мок для инстанса LogExceptionCommand, который
    будет создаваться в обработчиках исключений
    """
    instance_mock = Mock(spec_set=LogExceptionCommand)
    constructor_mock = Mock()
    constructor_mock.return_value = instance_mock

    monkeypatch.setattr(
        f"{LogExceptionCommand.__module__}.{LogExceptionCommand.__qualname__}.__new__",
        constructor_mock,
    )
    return instance_mock


def test_delayed_log_exception(
    mock_log_exception_command: Mock,
    exception_handler_store: ExceptionHandlerStore,
    event_loop: EventLoop,
) -> None:
    """
    Тест обработчика для логгирования исключения
    """
    exception_handler_store.register_handler(MockCommand, MockError, delayed_log_exception_handler)
    cmd = MockCommand()
    cmd.execute = Mock(side_effect=MockError)
    event_loop.put_command(cmd)
    event_loop.run_until_complete()

    mock_log_exception_command.execute.assert_called_once()


def test_delayed_first_retry(
    exception_handler_store: ExceptionHandlerStore,
    event_loop: EventLoop,
) -> None:
    """
    Тест обработчика для повторного добавления команд в очередь
    """
    exception_handler_store.register_handler(MockCommand, MockError, delayed_first_retry_handler)
    cmd = MockCommand()
    cmd.execute = Mock(side_effect=[MockError, None])

    event_loop.put_command(cmd)
    event_loop.run_until_complete()

    assert cmd.execute.call_count == 2


def test_one_retry_then_log(
    mock_log_exception_command: Mock,
    exception_handler_store: ExceptionHandlerStore,
    event_loop: EventLoop,
) -> None:
    """
    Тест стратегии: при первом выбросе исключения повторить команду,
    при повторном выбросе исключения записать информацию в лог
    """
    exception_handler_store.register_handler(MockCommand, MockError, delayed_first_retry_handler)
    exception_handler_store.register_default_command_handler(
        FirstRetryCommand, delayed_log_exception_handler
    )
    cmd = MockCommand()
    cmd.execute = Mock(side_effect=MockError)

    event_loop.put_command(cmd)
    event_loop.run_until_complete()

    assert cmd.execute.call_count == 2
    mock_log_exception_command.execute.assert_called_once()


def test_two_retries_then_log(
    mock_log_exception_command: Mock,
    exception_handler_store: ExceptionHandlerStore,
    event_loop: EventLoop,
) -> None:
    """
    Тест стратегии: повторить два раза, потом записать в лог
    """
    exception_handler_store.register_handler(MockCommand, MockError, delayed_first_retry_handler)
    exception_handler_store.register_handler(
        FirstRetryCommand, MockError, delayed_second_retry_handler
    )
    exception_handler_store.register_default_command_handler(
        SecondRetryCommand, delayed_log_exception_handler
    )
    cmd = MockCommand()
    cmd.execute = Mock(side_effect=MockError)

    event_loop.put_command(cmd)
    event_loop.run_until_complete()

    assert cmd.execute.call_count == 3
    mock_log_exception_command.execute.assert_called_once()
