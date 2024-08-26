from abc import ABC, abstractmethod
from typing import override

from loguru import logger

from app.core.command import ICommand
from app.game.value_types import Angle
from codegen.decorators import generate_adapter


@generate_adapter
class IRotatable(ABC):
    @abstractmethod
    def get_angle(self) -> Angle: ...
    @abstractmethod
    def set_angle(self, value: Angle) -> None: ...

    @abstractmethod
    def get_angular_velocity(self) -> Angle: ...


class RotateCommand(ICommand):
    def __init__(self, rotatable: IRotatable) -> None:
        self._rotatable = rotatable

    @override
    def execute(self) -> None:
        direction = self._rotatable.get_angle()
        velocity = self._rotatable.get_angular_velocity()
        logger.debug(f"Rotating {self._rotatable} with {direction=} and {velocity=}")
        self._rotatable.set_angle(direction + velocity)
