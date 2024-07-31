from collections.abc import Callable
from queue import Queue

from app.command import ICommand
from app.exception_handler import ExceptionHandlerStore


class GameLoop:
    def __init__(
        self,
        exception_handler_store: ExceptionHandlerStore,
    ) -> None:
        self._command_queue: Queue[ICommand] = Queue()
        self._exception_handler_store = exception_handler_store

    def put_command(self, cmd: ICommand) -> None:
        self._command_queue.put(cmd)

    def run_forever(self) -> None:
        self._run(lambda: False)

    def run_until_complete(self) -> None:
        self._run(lambda: self._command_queue.empty())

    def _run(self, stop_func: Callable[[], bool]) -> None:
        while not stop_func():
            cmd = self._command_queue.get()
            try:
                cmd.execute()
            except Exception as exc:
                self._exception_handler_store.create_handler(cmd, exc).execute()
