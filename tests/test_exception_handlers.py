from unittest.mock import Mock

import pytest

from app.exception_handlers import (
    FirstRetryCommand,
    LogExceptionCommand,
    SecondRetryCommand,
    delayed_first_retry_handler,
    delayed_log_exception_handler,
    delayed_second_retry_handler,
)
from app.game_state import game_state
from tests.mocks import MockCommand


class TestError(Exception): ...


@pytest.fixture(autouse=True)
def _reset_game_state() -> None:
    game_state.reset()


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


def test_delayed_log_exception(mock_log_exception_command: Mock) -> None:
    """
    Тест обработчика для логгирования исключения
    """
    game_state.exception_handler_store.register_handler(
        MockCommand, TestError, delayed_log_exception_handler
    )
    cmd = MockCommand()
    cmd.execute = Mock(side_effect=TestError)
    game_state.game_loop.put_command(cmd)
    game_state.game_loop.run_until_complete()

    mock_log_exception_command.execute.assert_called_once()


def test_delayed_first_retry() -> None:
    """
    Тест обработчика для повторного добавления команд в очередь
    """
    game_state.exception_handler_store.register_handler(
        MockCommand, TestError, delayed_first_retry_handler
    )
    cmd = MockCommand()
    cmd.execute = Mock(side_effect=[TestError, None])

    game_state.game_loop.put_command(cmd)
    game_state.game_loop.run_until_complete()

    assert cmd.execute.call_count == 2


def test_one_retry_then_log(mock_log_exception_command: Mock) -> None:
    """
    Тест стратегии: при первом выбросе исключения повторить команду,
    при повторном выбросе исключения записать информацию в лог
    """
    game_state.exception_handler_store.register_handler(
        MockCommand, TestError, delayed_first_retry_handler
    )
    game_state.exception_handler_store.register_default_command_handler(
        FirstRetryCommand, delayed_log_exception_handler
    )
    cmd = MockCommand()
    cmd.execute = Mock(side_effect=TestError)

    game_state.game_loop.put_command(cmd)
    game_state.game_loop.run_until_complete()

    assert cmd.execute.call_count == 2
    mock_log_exception_command.execute.assert_called_once()


def test_two_retries_then_log(mock_log_exception_command: Mock) -> None:
    """
    Тест стратегии: повторить два раза, потом записать в лог
    """
    game_state.exception_handler_store.register_handler(
        MockCommand, TestError, delayed_first_retry_handler
    )
    game_state.exception_handler_store.register_handler(
        FirstRetryCommand, TestError, delayed_second_retry_handler
    )
    game_state.exception_handler_store.register_default_command_handler(
        SecondRetryCommand, delayed_log_exception_handler
    )
    cmd = MockCommand()
    cmd.execute = Mock(side_effect=TestError)

    game_state.game_loop.put_command(cmd)
    game_state.game_loop.run_until_complete()

    assert cmd.execute.call_count == 3
    mock_log_exception_command.execute.assert_called_once()
