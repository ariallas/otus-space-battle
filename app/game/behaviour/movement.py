from abc import ABC, abstractmethod
from typing import override

from loguru import logger

from app.core.command import ICommand
from app.game.value_types import Vector
from codegen.decorators import generate_adapter


@generate_adapter
class IMovable(ABC):
    @abstractmethod
    def get_position(self) -> Vector: ...

    @abstractmethod
    def set_position(self, value: Vector) -> None: ...

    @abstractmethod
    def get_velocity(self) -> Vector: ...


class MoveCommand(ICommand):
    def __init__(self, movable: IMovable) -> None:
        self._movable = movable

    @override
    def execute(self) -> None:
        pos = self._movable.get_position()
        velocity = self._movable.get_velocity()
        logger.debug(f"Moving {self._movable} with {pos=} and {velocity=}")
        self._movable.set_position(pos + velocity)


@generate_adapter
class ICanChangeVelocity(ABC):
    @abstractmethod
    def set_velocity(self, value: Vector) -> None: ...

    @abstractmethod
    def get_velocity(self) -> Vector: ...
