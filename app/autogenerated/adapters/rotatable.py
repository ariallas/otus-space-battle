from typing import override

from app.core.command import ICommand
from app.core.ioc import IoC
from app.game.behaviour.rotation import IRotatable
from app.game.uobject import UObject
from app.game.value_types import Angle


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
