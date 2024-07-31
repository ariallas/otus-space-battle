from abc import ABC, abstractmethod
from typing import override

from loguru import logger

from app.command import ICommand
from app.game_object import UObject
from app.value_types import Angle, Vector


class IMovable(ABC):
    @abstractmethod
    def get_position(self) -> Vector: ...
    @abstractmethod
    def set_position(self, v: Vector) -> None: ...

    @abstractmethod
    def get_velocity(self) -> Vector: ...


class MovableAdapter(IMovable):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def get_position(self) -> Vector:
        return self._uobject.get_property("movable_position")

    @override
    def set_position(self, v: Vector) -> None:
        return self._uobject.set_property("movable_position", v)

    @override
    def get_velocity(self) -> Vector:
        angle: Angle = self._uobject.get_property("movable_angle")
        velocity: int = self._uobject.get_property("movable_abs_velocity")

        return Vector.from_angle_and_length(angle, velocity)


class Move(ICommand):
    def __init__(self, movable: IMovable) -> None:
        self._movable = movable

    @override
    def execute(self) -> None:
        pos = self._movable.get_position()
        velocity = self._movable.get_velocity()
        logger.debug(f"Moving {self._movable} with {pos=} and {velocity=}")
        self._movable.set_position(pos + velocity)
