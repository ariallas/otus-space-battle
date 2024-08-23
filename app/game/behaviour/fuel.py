from abc import ABC, abstractmethod
from typing import override

from loguru import logger

from app.core.command import CommandError, ICommand, LambdaCommand
from app.core.ioc import IoC
from app.game.uobject import UObject


class IConsumesFuel(ABC):
    @abstractmethod
    def get_amount(self) -> int: ...
    @abstractmethod
    def set_amount(self, fuel_amount: int) -> None: ...

    @abstractmethod
    def get_consumption(self) -> int: ...


def ioc_setup_iconsumesfuel() -> None:
    def _get_amount(uobj: UObject) -> int:
        return uobj.get_property("fuel_amount")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IConsumesFuel.amount.Get",
        _get_amount,
    ).execute()

    def _set_amount(uobj: UObject, fuel_amount: int) -> None:
        uobj.set_property("fuel_amount", fuel_amount)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IConsumesFuel.amount.Set",
        LambdaCommand(_set_amount).setup,
    ).execute()

    def _get_consumption(uobj: UObject) -> int:
        return uobj.get_property("fuel_consumption")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IConsumesFuel.consumption.Get",
        _get_consumption,
    ).execute()


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
