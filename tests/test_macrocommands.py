from unittest.mock import Mock

import pytest

from app.command import ICommand, MacroCommand
from app.exceptions import CommandError
from app.fuel import BurnFuelCommand, CheckFuelCommand, UsesFuelAdapter
from app.movement import MovableAdapter, MoveCommand
from app.value_types import Vector
from tests.mocks import MockUObject
from tests.test_fuel import make_fuel_consumer_uobject
from tests.test_movement import make_movable_uobject


class TstError(Exception): ...


@pytest.fixture()
def mock_commands() -> list[Mock]:
    commands = [Mock() for _ in range(10)]
    for command in commands:
        command.execute = Mock()
    return commands


def test_macrocommand() -> None:
    commands = [Mock(spec_set=ICommand) for _ in range(10)]
    mc = MacroCommand(commands)  # pyright: ignore[reportArgumentType]
    mc.execute()
    for cmd in commands:
        cmd.execute.assert_called_once()


def test_macrocommand_error() -> None:
    commands = [Mock(spec_set=ICommand) for _ in range(10)]
    commands[5].execute.side_effect = TstError
    mc = MacroCommand(commands)  # pyright: ignore[reportArgumentType]
    with pytest.raises(CommandError):
        mc.execute()


def test_move_and_burn_fuel() -> None:
    uobj = MockUObject()
    make_movable_uobject(Vector(0, 0), Vector(1, 0), uobj)
    make_fuel_consumer_uobject(10, 5, uobj)

    movable = MovableAdapter(uobj)
    fuel_consumer = UsesFuelAdapter(uobj)

    commands: list[ICommand] = [
        CheckFuelCommand(fuel_consumer),
        MoveCommand(movable),
        BurnFuelCommand(fuel_consumer),
    ]
    MacroCommand(commands).execute()

    assert movable.get_position() == Vector(1, 0)
    assert fuel_consumer.get_fuel_amount() == 5


def test_move_and_burn_fuel_error() -> None:
    uobj = MockUObject()
    make_movable_uobject(Vector(0, 0), Vector(1, 0), uobj)
    make_fuel_consumer_uobject(10, 11, uobj)

    movable = MovableAdapter(uobj)
    fuel_consumer = UsesFuelAdapter(uobj)

    commands: list[ICommand] = [
        CheckFuelCommand(fuel_consumer),
        MoveCommand(movable),
        BurnFuelCommand(fuel_consumer),
    ]
    with pytest.raises(CommandError):
        MacroCommand(commands).execute()
