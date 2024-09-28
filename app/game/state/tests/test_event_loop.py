import threading
from dataclasses import dataclass
from typing import Any
from unittest.mock import Mock

import pytest

from app.core.command import ICommand
from app.core.exception_handler_store import ExceptionHandlerStore
from app.core.ioc import IoC
from app.game.setup.state import ioc_setup_event_loop, ioc_setup_exception_handler_store
from app.game.state.event_loop import (
    EventLoop,
    HardStopEventLoopCommand,
    RunEventLoopInThreadCommand,
    SoftStopEventLoopCommand,
)
from app.game.state.exception_handlers import DelayedCommand


@dataclass
class EventLoopSetup:
    event_loop: EventLoop
    scope: Any


@pytest.fixture(autouse=True)
def el_setup() -> EventLoopSetup:
    ioc_setup_exception_handler_store()

    el_scope = IoC.resolve("IoC.Scope.Create", "EventLoop")
    IoC[ICommand].resolve("IoC.Scope.Current.Set", el_scope).execute()
    ioc_setup_event_loop()
    event_loop = IoC[EventLoop].resolve("EventLoop")
    IoC[ICommand].resolve("IoC.Scope.Current.Clear").execute()

    return EventLoopSetup(event_loop=event_loop, scope=el_scope)


@pytest.fixture()
def exception_handler_store() -> ExceptionHandlerStore:
    return IoC[ExceptionHandlerStore].resolve("ExceptionHandlerStore")


def test_run_event_loop(el_setup: EventLoopSetup) -> None:
    cmd = Mock()
    event = threading.Event()
    cmd.execute = event.set

    el_setup.event_loop.put_command(cmd)

    RunEventLoopInThreadCommand(el_setup.event_loop, el_setup.scope).execute()
    event.wait()

    el_setup.event_loop.put_command(HardStopEventLoopCommand(el_setup.event_loop))


def test_delayed_command_in_event_loop(el_setup: EventLoopSetup) -> None:
    mock_cmd = Mock()
    delayed_cmd = DelayedCommand(mock_cmd)

    event = threading.Event()
    mock_cmd.execute = event.set

    el_setup.event_loop.put_command(delayed_cmd)

    RunEventLoopInThreadCommand(el_setup.event_loop, el_setup.scope).execute()
    event.wait()

    el_setup.event_loop.put_command(HardStopEventLoopCommand(el_setup.event_loop))


def test_hard_stop(el_setup: EventLoopSetup) -> None:
    event_loop = el_setup.event_loop

    cmd1 = Mock()
    cmd2 = Mock()

    event_loop.put_command(cmd1)
    event_loop.put_command(HardStopEventLoopCommand(event_loop))
    event_loop.put_command(cmd2)

    event = threading.Event()
    event_loop.add_after_hook(event.set)

    RunEventLoopInThreadCommand(event_loop, el_setup.scope).execute()

    event.wait()
    cmd1.execute.assert_called_once()
    cmd2.execute.assert_not_called()


def test_soft_stop(el_setup: EventLoopSetup) -> None:
    event_loop = el_setup.event_loop

    cmd1 = Mock()
    cmd2 = Mock()

    event_loop.put_command(cmd1)
    event_loop.put_command(SoftStopEventLoopCommand(event_loop))
    event_loop.put_command(cmd2)

    event = threading.Event()
    event_loop.add_after_hook(event.set)

    RunEventLoopInThreadCommand(event_loop, el_setup.scope).execute()

    event.wait()
    cmd1.execute.assert_called_once()
    cmd2.execute.assert_called_once()
