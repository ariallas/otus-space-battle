from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from queue import Empty, Queue
from typing import Any, override

from loguru import logger

from app.core.command import ICommand
from app.core.ioc import IoC


class GameCommand(ICommand):
    def __init__(
        self,
        id_: int,
        queue: Queue[ICommand],
        quant: timedelta,
        scope: Any,
        init: Callable[[], None],
    ) -> None:
        self._id = id_
        self._queue = queue
        self._quant = quant
        self._scope = scope

        IoC[ICommand].resolve("IoC.Scope.Current.Set", self._scope).execute()
        init()

    @override
    def execute(self) -> None:
        logger.debug(f"Starting tick for game {self._id}")
        IoC[ICommand].resolve("IoC.Scope.Current.Set", self._scope).execute()

        start = datetime.now(UTC)
        while datetime.now(UTC) - start < self._quant:
            try:
                cmd = self._queue.get(timeout=self._quant.total_seconds())
                cmd.execute()
            except Empty:
                pass

        logger.debug(f"Done with tick for game {self._id}")
