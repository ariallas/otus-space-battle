from abc import ABC, abstractmethod
from typing import override

from loguru import logger

from app.game_object import UObject
from app.value_types import Angle


class IRotatable(ABC):
    @abstractmethod
    def get_angle(self) -> Angle: ...
    @abstractmethod
    def set_angle(self, a: Angle) -> None: ...

    # В слайдах лекции (слайд 28) angular_velocity почему-то хранилась в int,
    # хотя у нас есть класс для представления угла. Вроде бы
    # логично и angular_velocity хранить как Angle - поправьте, если не так
    @abstractmethod
    def get_angular_velocity(self) -> Angle: ...


class RotatableAdapter(IRotatable):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def get_angle(self) -> Angle:
        return self._uobject.get_property("rotatable_angle")

    @override
    def set_angle(self, a: Angle) -> None:
        return self._uobject.set_property("rotatable_angle", a)

    @override
    def get_angular_velocity(self) -> Angle:
        return self._uobject.get_property("rotatable_angular_velocity")


class Rotate:
    def __init__(self, rotatable: IRotatable) -> None:
        self._rotatable = rotatable

    def execute(self) -> None:
        direction = self._rotatable.get_angle()
        velocity = self._rotatable.get_angular_velocity()
        logger.debug(f"Rotating {self._rotatable} with {direction=} and {velocity=}")
        self._rotatable.set_angle(direction + velocity)
