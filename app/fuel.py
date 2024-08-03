from abc import ABC, abstractmethod
from typing import override

from loguru import logger

from app.command import ICommand
from app.exceptions import CommandError
from app.game_object import UObject


class IConsumesFuel(ABC):
    @abstractmethod
    def get_fuel_amount(self) -> int: ...
    @abstractmethod
    def set_fuel_amount(self, f: int) -> None: ...

    @abstractmethod
    def get_fuel_consumption(self) -> int: ...


class UsesFuelAdapter(IConsumesFuel):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def get_fuel_amount(self) -> int:
        return self._uobject.get_property("fuel_amount")

    @override
    def set_fuel_amount(self, f: int) -> None:
        return self._uobject.set_property("fuel_amount", f)

    @override
    def get_fuel_consumption(self) -> int:
        return self._uobject.get_property("fuel_consumption")


def _raise_fuel_exception(current: int, required: int) -> None:
    raise CommandError(f"Not enough fuel: has {current} fuel, needs {required}")


class CheckFuelCommand(ICommand):
    def __init__(self, consumer: IConsumesFuel) -> None:
        self._consumer = consumer

    @override
    def execute(self) -> None:
        current = self._consumer.get_fuel_amount()
        required = self._consumer.get_fuel_consumption()
        logger.debug(f"Checking if {self._consumer} has enough fuel: {current=}, {required=}")
        if current < required:
            _raise_fuel_exception(current, required)


class BurnFuelCommand(ICommand):
    def __init__(self, consumer: IConsumesFuel) -> None:
        self._consumer = consumer

    @override
    def execute(self) -> None:
        current = self._consumer.get_fuel_amount()
        required = self._consumer.get_fuel_consumption()
        logger.debug(f"Burning fuel for {self._consumer}: {current=}, {required=}")
        if current < required:
            _raise_fuel_exception(current, required)
        self._consumer.set_fuel_amount(current - required)
