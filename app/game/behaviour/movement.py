from abc import ABC, abstractmethod
from typing import override

from loguru import logger

from app.core.command import ICommand, LambdaCommand
from app.core.ioc import IoC
from app.game.uobject import UObject
from app.game.value_types import Angle, Vector


class IMovable(ABC):
    @abstractmethod
    def get_position(self) -> Vector: ...

    @abstractmethod
    def set_position(self, value: Vector) -> None: ...

    @abstractmethod
    def get_velocity(self) -> Vector: ...


def ioc_setup_imovable() -> None:
    def _get_position(uobj: UObject) -> Vector:
        return uobj.get_property("movable_position")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IMovable.position.Get",
        _get_position,
    ).execute()

    def _set_position(uobj: UObject, v: Vector) -> None:
        uobj.set_property("movable_position", v)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IMovable.position.Set",
        LambdaCommand(_set_position).setup,
    ).execute()

    def _get_velocity(uobj: UObject) -> Vector:
        angle: Angle = uobj.get_property("movable_angle")
        velocity: int = uobj.get_property("movable_abs_velocity")
        return Vector.from_angle_and_length(angle, velocity)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IMovable.velocity.Get",
        _get_velocity,
    ).execute()


class MoveCommand(ICommand):
    def __init__(self, movable: IMovable) -> None:
        self._movable = movable

    @override
    def execute(self) -> None:
        pos = self._movable.get_position()
        velocity = self._movable.get_velocity()
        logger.debug(f"Moving {self._movable} with {pos=} and {velocity=}")
        self._movable.set_position(pos + velocity)


class ICanChangeVelocity(ABC):
    @abstractmethod
    def set_velocity(self, value: Vector) -> None: ...

    @abstractmethod
    def get_velocity(self) -> Vector: ...


def ioc_setup_icanchangevelocity() -> None:
    def _get_velocity(uobj: UObject) -> Vector:
        angle: Angle = uobj.get_property("movable_angle")
        velocity: int = uobj.get_property("movable_abs_velocity")
        return Vector.from_angle_and_length(angle, velocity)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "ICanChangeVelocity.velocity.Get",
        _get_velocity,
    ).execute()

    def _set_velocity(uobj: UObject, v: Vector) -> None:
        angle = v.get_angle()
        length = v.get_length()
        uobj.set_property("movable_angle", angle)
        uobj.set_property("movable_abs_velocity", length)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "ICanChangeVelocity.velocity.Set",
        LambdaCommand(_set_velocity).setup,
    ).execute()
