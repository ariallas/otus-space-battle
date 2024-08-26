from typing import override

from app.core.command import ICommand
from app.core.ioc import IoC
from app.game.behaviour.fuel import IConsumesFuel
from app.game.uobject import UObject


class ConsumesFuelAdapter(IConsumesFuel):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def get_amount(self) -> int:
        return IoC[int].resolve(
            "IConsumesFuel.amount.Get",
            self._uobject,
        )

    @override
    def get_consumption(self) -> int:
        return IoC[int].resolve(
            "IConsumesFuel.consumption.Get",
            self._uobject,
        )

    @override
    def set_amount(self, value: int) -> None:
        IoC[ICommand].resolve(
            "IConsumesFuel.amount.Set",
            self._uobject,
            value,
        ).execute()
