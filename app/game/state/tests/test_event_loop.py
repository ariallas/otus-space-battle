import threading
from unittest.mock import Mock

import pytest

from app.core.exception_handler_store import ExceptionHandlerStore
from app.core.ioc import IoC
from app.game.setup.state import ioc_setup_event_loop, ioc_setup_exception_handler_store
from app.game.state.event_loop import (
    EventLoop,
    HardStopEventLoopCommand,
    RunEventLoopInThreadCommand,
    SoftStopEventLoopCommand,
)


@pytest.fixture(autouse=True)
def _ioc_setup() -> None:
    ioc_setup_exception_handler_store()
    ioc_setup_event_loop()


@pytest.fixture()
def exception_handler_store() -> ExceptionHandlerStore:
    return IoC[ExceptionHandlerStore].resolve("ExceptionHandlerStore")


@pytest.fixture()
def event_loop() -> EventLoop:
    return IoC[EventLoop].resolve("EventLoop")


def test_run_event_loop(event_loop: EventLoop) -> None:
    cmd = Mock()
    event = threading.Event()
    cmd.execute = event.set

    event_loop.put_command(cmd)

    RunEventLoopInThreadCommand(event_loop).execute()
    event.wait()

    event_loop.put_command(HardStopEventLoopCommand(event_loop))


def test_hard_stop(event_loop: EventLoop) -> None:
    cmd1 = Mock()
    cmd2 = Mock()

    event_loop.put_command(cmd1)
    event_loop.put_command(HardStopEventLoopCommand(event_loop))
    event_loop.put_command(cmd2)

    event = threading.Event()
    event_loop.add_after_hook(event.set)

    RunEventLoopInThreadCommand(event_loop).execute()

    event.wait()
    cmd1.execute.assert_called_once()
    cmd2.execute.assert_not_called()


def test_soft_stop(event_loop: EventLoop) -> None:
    cmd1 = Mock()
    cmd2 = Mock()

    event_loop.put_command(cmd1)
    event_loop.put_command(SoftStopEventLoopCommand(event_loop))
    event_loop.put_command(cmd2)

    event = threading.Event()
    event_loop.add_after_hook(event.set)

    RunEventLoopInThreadCommand(event_loop).execute()

    event.wait()
    cmd1.execute.assert_called_once()
    cmd2.execute.assert_called_once()
