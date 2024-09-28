from loguru import logger

from app.core.command import ICommand
from app.core.ioc import IoC
from app.game.state.event_loop import EventLoop


class DelayedCommand(ICommand):
    def __init__(self, cmd: ICommand) -> None:
        self._cmd = cmd

    def execute(self) -> None:
        event_loop = IoC[EventLoop].resolve("EventLoop")
        return event_loop.put_command(self._cmd)


class InjectableCommand(ICommand):
    def set_cmd(self, cmd: ICommand) -> None:
        self._cmd = cmd

    def execute(self) -> None:
        self._cmd.execute()


class LogExceptionCommand(ICommand):
    def __init__(self, cmd: ICommand, exc: Exception) -> None:
        self._cmd = cmd
        self._exc = exc

    def execute(self) -> None:
        logger.error(f"Exception while executing {self._cmd}: {self._exc}")


def delayed_log_exception_handler(cmd: ICommand, exc: Exception) -> ICommand:
    return DelayedCommand(LogExceptionCommand(cmd, exc))


class FirstRetryCommand(ICommand):
    def __init__(self, cmd: ICommand) -> None:
        self._cmd = cmd

    def execute(self) -> None:
        self._cmd.execute()


def delayed_first_retry_handler(cmd: ICommand, _exc: Exception) -> ICommand:
    return DelayedCommand(FirstRetryCommand(cmd))


class SecondRetryCommand(ICommand):
    def __init__(self, cmd: ICommand) -> None:
        self._cmd = cmd

    def execute(self) -> None:
        self._cmd.execute()


def delayed_second_retry_handler(cmd: ICommand, _exc: Exception) -> ICommand:
    return DelayedCommand(SecondRetryCommand(cmd))
