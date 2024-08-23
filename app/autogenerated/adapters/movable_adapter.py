from typing import override

from app.core.command import ICommand
from app.core.ioc import IoC
from app.game.behaviour.movement import IMovable
from app.game.uobject import UObject
from app.game.value_types import Vector


class MovableAdapter(IMovable):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def get_position(self) -> Vector:
        return IoC[Vector].resolve("IMovable.position.Get", self._uobject)

    @override
    def get_velocity(self) -> Vector:
        return IoC[Vector].resolve("IMovable.velocity.Get", self._uobject)

    @override
    def set_position(self, value: Vector) -> None:
        return IoC[ICommand].resolve("IMovable.position.Set", self._uobject, value).execute()
