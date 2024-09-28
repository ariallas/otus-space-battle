from collections.abc import Callable
from queue import Queue
from threading import Thread
from typing import Any, override

from loguru import logger

from app.core.command import ICommand
from app.core.exception_handler_store import ExceptionHandlerStore
from app.core.ioc import IoC

HookFunc = Callable[[], None]


class EventLoop:
    def __init__(
        self,
        exception_handler_store: ExceptionHandlerStore,
    ) -> None:
        self._command_queue: Queue[ICommand] = Queue()
        self._exception_handler_store = exception_handler_store

        self._before_hooks: list[HookFunc] = []
        self._after_hooks: list[HookFunc] = []

        self._stop_func: Callable[[], bool] = lambda: False

    def add_before_hook(self, hook: HookFunc) -> None:
        self._before_hooks.append(hook)

    def add_after_hook(self, hook: HookFunc) -> None:
        self._after_hooks.append(hook)

    def put_command(self, cmd: ICommand) -> None:
        self._command_queue.put(cmd)

    def run_forever(self) -> None:
        self._run()

    def run_until_complete(self) -> None:
        self._stop_func = lambda: self._command_queue.empty()
        self._run()

    def set_hard_stop(self) -> None:
        self._stop_func = lambda: True

    def set_soft_stop(self) -> None:
        self._stop_func = lambda: self._command_queue.empty()

    def _run(self) -> None:
        logger.info("Starting event loop")
        for hook in self._before_hooks:
            hook()

        while not self._stop_func():
            cmd = self._command_queue.get()
            try:
                cmd.execute()
            except Exception as exc:
                self._exception_handler_store.create_handler_command(cmd, exc).execute()

        for hook in self._after_hooks:
            hook()
        logger.info("Done with event loop")


class RunEventLoopInThreadCommand(ICommand):
    def __init__(self, event_loop: EventLoop, scope: Any) -> None:
        self._event_loop = event_loop
        self._scope = scope

    @override
    def execute(self) -> None:
        thread = Thread(target=self._run)
        thread.start()

    def _run(self) -> None:
        IoC[ICommand].resolve("IoC.Scope.Current.Set", self._scope).execute()
        self._event_loop.run_forever()


class SoftStopEventLoopCommand(ICommand):
    def __init__(self, event_loop: EventLoop) -> None:
        self._event_loop = event_loop

    @override
    def execute(self) -> None:
        self._event_loop.set_soft_stop()


class HardStopEventLoopCommand(ICommand):
    def __init__(self, event_loop: EventLoop) -> None:
        self._event_loop = event_loop

    @override
    def execute(self) -> None:
        self._event_loop.set_hard_stop()
