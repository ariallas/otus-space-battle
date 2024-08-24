from abc import ABC, abstractmethod
from typing import override

from loguru import logger

from app.core.command import CommandError, ICommand
from codegen.decorators import generate_adapter


@generate_adapter
class IConsumesFuel(ABC):
    @abstractmethod
    def get_amount(self) -> int: ...
    @abstractmethod
    def set_amount(self, value: int) -> None: ...

    @abstractmethod
    def get_consumption(self) -> int: ...


class CheckFuelCommand(ICommand):
    def __init__(self, consumer: IConsumesFuel) -> None:
        self._consumer = consumer

    @override
    def execute(self) -> None:
        current = self._consumer.get_amount()
        required = self._consumer.get_consumption()
        logger.debug(f"Checking if {self._consumer} has enough fuel: {current=}, {required=}")
        if current < required:
            raise CommandError(f"Not enough fuel: has {current} fuel, needs {required}")


class BurnFuelCommand(ICommand):
    def __init__(self, consumer: IConsumesFuel) -> None:
        self._consumer = consumer

    @override
    def execute(self) -> None:
        current = self._consumer.get_amount()
        required = self._consumer.get_consumption()
        logger.debug(f"Burning fuel for {self._consumer}: {current=}, {required=}")
        self._consumer.set_amount(current - required)
