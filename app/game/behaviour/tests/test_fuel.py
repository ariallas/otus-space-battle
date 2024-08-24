import pytest

from app.core.command import CommandError
from app.core.ioc import IoC
from app.game.behaviour.fuel import (
    BurnFuelCommand,
    CheckFuelCommand,
    IConsumesFuel,
)
from app.game.setup.adapters import ioc_setup_adapters
from app.game.setup.behaviour import ioc_setup_iconsumesfuel
from app.game.uobject import UObject
from tests.mocks import MockUObject


@pytest.fixture(autouse=True)
def _ioc_setup() -> None:
    ioc_setup_iconsumesfuel()
    ioc_setup_adapters()


def make_fuel_consumer_uobject(
    amount: int, consumption: int, uobj: UObject | None = None
) -> UObject:
    if not uobj:
        uobj = MockUObject()
    uobj.set_property("fuel_amount", amount)
    uobj.set_property("fuel_consumption", consumption)
    return uobj


def test_check_fuel() -> None:
    uobj = make_fuel_consumer_uobject(10, 5)
    consumer = IoC[IConsumesFuel].resolve("Adapter", IConsumesFuel, uobj)
    CheckFuelCommand(consumer).execute()

    uobj = make_fuel_consumer_uobject(10, 11)
    consumer = IoC[IConsumesFuel].resolve("Adapter", IConsumesFuel, uobj)
    with pytest.raises(CommandError):
        CheckFuelCommand(consumer).execute()


def test_burn_fuel() -> None:
    uobj = make_fuel_consumer_uobject(10, 5)
    consumer = IoC[IConsumesFuel].resolve("Adapter", IConsumesFuel, uobj)
    BurnFuelCommand(consumer).execute()
    assert consumer.get_amount() == 5
    BurnFuelCommand(consumer).execute()
    assert consumer.get_amount() == 0
