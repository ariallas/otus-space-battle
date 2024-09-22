from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from queue import Queue
from typing import Any, override

from app.core.command import ICommand
from app.core.ioc import IoC


class GameCommand(ICommand):
    def __init__(
        self,
        queue: Queue[ICommand],
        quant: timedelta,
        scope: Any,
        init: Callable[[], None],
    ) -> None:
        self._queue = queue
        self._quant = quant
        self._scope = scope

        IoC[ICommand].resolve("IoC.Scope.Current.Set", self._scope).execute()
        init()

    @override
    def execute(self) -> None:
        IoC[ICommand].resolve("IoC.Scope.Current.Set", self._scope).execute()

        start = datetime.now(UTC)
        while datetime.now(UTC) - start < self._quant:
            if self._queue.empty():
                return
            cmd = self._queue.get()
            cmd.execute()
