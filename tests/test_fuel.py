import pytest

from app.exceptions import CommandError
from app.fuel import BurnFuelCommand, CheckFuelCommand, UsesFuelAdapter
from app.game_object import UObject
from tests.mocks import MockUObject


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
    CheckFuelCommand(UsesFuelAdapter(uobj)).execute()

    uobj = make_fuel_consumer_uobject(10, 11)
    with pytest.raises(CommandError):
        CheckFuelCommand(UsesFuelAdapter(uobj)).execute()


def test_burn_fuel() -> None:
    uobj = make_fuel_consumer_uobject(10, 5)
    consumer = UsesFuelAdapter(uobj)
    BurnFuelCommand(consumer).execute()
    assert consumer.get_fuel_amount() == 5
    BurnFuelCommand(consumer).execute()
    assert consumer.get_fuel_amount() == 0

    with pytest.raises(CommandError):
        BurnFuelCommand(UsesFuelAdapter(uobj)).execute()
