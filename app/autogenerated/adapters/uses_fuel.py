from typing import override

from app.core.command import ICommand
from app.core.ioc import IoC
from app.game.behaviour.fuel import IConsumesFuel
from app.game.uobject import UObject


class UsesFuelAdapter(IConsumesFuel):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def get_amount(self) -> int:
        return IoC[int].resolve("IConsumesFuel.amount.Get", self._uobject)

    @override
    def set_amount(self, fuel_amount: int) -> None:
        return (
            IoC[ICommand].resolve("IConsumesFuel.amount.Set", self._uobject, fuel_amount).execute()
        )

    @override
    def get_consumption(self) -> int:
        return IoC[int].resolve("IConsumesFuel.consumption.Get", self._uobject)
