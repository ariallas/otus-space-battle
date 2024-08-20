from abc import ABC, abstractmethod
from typing import override

from loguru import logger

from app.core.command import ICommand, LambdaCommand
from app.core.ioc import IoC
from app.game.uobject import UObject
from app.game.value_types import Angle


class IRotatable(ABC):
    @abstractmethod
    def get_angle(self) -> Angle: ...
    @abstractmethod
    def set_angle(self, a: Angle) -> None: ...

    @abstractmethod
    def get_angular_velocity(self) -> Angle: ...


def ioc_setup_irotatable() -> None:
    def _get_angle(uobj: UObject) -> Angle:
        return uobj.get_property("rotatable_angle")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IRotatable.angle.Get",
        _get_angle,
    ).execute()

    def _set_angle(uobj: UObject, a: Angle) -> None:
        uobj.set_property("rotatable_angle", a)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IRotatable.angle.Set",
        LambdaCommand(_set_angle).setup,
    ).execute()

    def _get_angular_velocity(uobj: UObject) -> Angle:
        return uobj.get_property("rotatable_angular_velocity")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IRotatable.angular_velocity.Get",
        _get_angular_velocity,
    ).execute()


class RotatableAdapter(IRotatable):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def get_angle(self) -> Angle:
        return IoC[Angle].resolve("IRotatable.angle.Get", self._uobject)

    @override
    def set_angle(self, a: Angle) -> None:
        return IoC[ICommand].resolve("IRotatable.angle.Set", self._uobject, a).execute()

    @override
    def get_angular_velocity(self) -> Angle:
        return IoC[Angle].resolve("IRotatable.angular_velocity.Get", self._uobject)


class RotateCommand(ICommand):
    def __init__(self, rotatable: IRotatable) -> None:
        self._rotatable = rotatable

    @override
    def execute(self) -> None:
        direction = self._rotatable.get_angle()
        velocity = self._rotatable.get_angular_velocity()
        logger.debug(f"Rotating {self._rotatable} with {direction=} and {velocity=}")
        self._rotatable.set_angle(direction + velocity)
