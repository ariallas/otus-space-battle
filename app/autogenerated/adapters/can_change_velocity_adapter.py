from typing import override

from app.core.command import ICommand
from app.core.ioc import IoC
from app.game.behaviour.movement import ICanChangeVelocity
from app.game.uobject import UObject
from app.game.value_types import Vector


class CanChangeVelocityAdapter(ICanChangeVelocity):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def get_velocity(self) -> Vector:
        return IoC[Vector].resolve(
            "ICanChangeVelocity.velocity.Get",
            self._uobject,
        )

    @override
    def set_velocity(self, value: Vector) -> None:
        IoC[ICommand].resolve(
            "ICanChangeVelocity.velocity.Set",
            self._uobject,
            value,
        ).execute()
