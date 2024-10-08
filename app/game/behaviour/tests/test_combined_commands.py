from unittest.mock import Mock

import pytest

from app.core.command import CommandError, ICommand, MacroCommand
from app.core.ioc import IoC
from app.game.behaviour.combined_commands import AdjustVelocityToRotationCommand
from app.game.behaviour.fuel import (
    BurnFuelCommand,
    CheckFuelCommand,
    IConsumesFuel,
)
from app.game.behaviour.movement import (
    ICanChangeVelocity,
    IMovable,
    MoveCommand,
)
from app.game.behaviour.rotation import IRotatable, RotateCommand
from app.game.behaviour.tests.test_fuel import make_fuel_consumer_uobject
from app.game.behaviour.tests.test_movement import make_movable_uobject
from app.game.behaviour.tests.test_rotation import make_rotatable_uobject
from app.game.setup.adapters import ioc_setup_adapters
from app.game.setup.behaviour import (
    ioc_setup_icanchangevelocity,
    ioc_setup_iconsumesfuel,
    ioc_setup_imovable,
    ioc_setup_irotatable,
)
from app.game.value_types import Angle, Vector
from tests.mocks import MockUObject


@pytest.fixture(autouse=True)
def _ioc_setup() -> None:
    ioc_setup_imovable()
    ioc_setup_irotatable()
    ioc_setup_icanchangevelocity()
    ioc_setup_iconsumesfuel()
    ioc_setup_adapters()


class TstError(Exception): ...


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
    make_movable_uobject(position=Vector(0, 0), velocity=Vector(1, 0), uobj=uobj)
    make_fuel_consumer_uobject(amount=10, consumption=5, uobj=uobj)

    movable = IoC[IMovable].resolve("Adapter", IMovable, uobj)
    fuel_consumer = IoC[IConsumesFuel].resolve("Adapter", IConsumesFuel, uobj)

    commands: list[ICommand] = [
        CheckFuelCommand(fuel_consumer),
        MoveCommand(movable),
        BurnFuelCommand(fuel_consumer),
    ]
    MacroCommand(commands).execute()

    assert movable.get_position() == Vector(1, 0)
    assert fuel_consumer.get_amount() == 5


def test_move_and_burn_fuel_error() -> None:
    uobj = MockUObject()
    make_movable_uobject(position=Vector(0, 0), velocity=Vector(1, 0), uobj=uobj)
    make_fuel_consumer_uobject(amount=10, consumption=11, uobj=uobj)

    movable = IoC[IMovable].resolve("Adapter", IMovable, uobj)
    fuel_consumer = IoC[IConsumesFuel].resolve("Adapter", IConsumesFuel, uobj)

    commands: list[ICommand] = [
        CheckFuelCommand(fuel_consumer),
        MoveCommand(movable),
        BurnFuelCommand(fuel_consumer),
    ]
    with pytest.raises(CommandError):
        MacroCommand(commands).execute()


DIRECTIONS_NUMBER = 72


def test_adjust_velocity_to_rotation() -> None:
    uobj = MockUObject()
    make_movable_uobject(position=Vector(0, 0), velocity=Vector(1, 0), uobj=uobj)
    make_rotatable_uobject(
        angle=Angle.from_degrees(90, DIRECTIONS_NUMBER),
        angular_velocity=Angle.from_degrees(90, DIRECTIONS_NUMBER),
        uobj=uobj,
    )

    can_change_velocity = IoC[ICanChangeVelocity].resolve("Adapter", ICanChangeVelocity, uobj)

    adjust_velocity_cmd = AdjustVelocityToRotationCommand(
        IoC[IRotatable].resolve("Adapter", IRotatable, uobj), can_change_velocity
    )
    adjust_velocity_cmd.execute()

    assert can_change_velocity.get_velocity() == Vector(0, 1)


def test_adjust_velocity_to_rotation_nonmovable_object() -> None:
    """
    Попытка применить AdjustVelocityToRotationCommand к объекту,
    который не может двигаться (я так понял, ошибки НЕ должно быть)
    """
    uobj = MockUObject()
    make_rotatable_uobject(
        angle=Angle.from_degrees(90, DIRECTIONS_NUMBER),
        angular_velocity=Angle.from_degrees(90, DIRECTIONS_NUMBER),
        uobj=uobj,
    )

    adjust_velocity_cmd = AdjustVelocityToRotationCommand(
        IoC[IRotatable].resolve("Adapter", IRotatable, uobj),
        IoC[ICanChangeVelocity].resolve("Adapter", ICanChangeVelocity, uobj),
    )
    adjust_velocity_cmd.execute()


def test_rotate_and_adjust_velocity_to_rotation() -> None:
    uobj = MockUObject()
    make_movable_uobject(position=Vector(0, 0), velocity=Vector(1, 0), uobj=uobj)
    make_rotatable_uobject(
        angle=Angle.from_degrees(90, DIRECTIONS_NUMBER),
        angular_velocity=Angle.from_degrees(90, DIRECTIONS_NUMBER),
        uobj=uobj,
    )

    can_change_velocity = IoC[ICanChangeVelocity].resolve("Adapter", ICanChangeVelocity, uobj)
    rotatable = IoC[IRotatable].resolve("Adapter", IRotatable, uobj)

    commands: list[ICommand] = [
        RotateCommand(rotatable),
        AdjustVelocityToRotationCommand(rotatable, can_change_velocity),
    ]
    MacroCommand(commands).execute()

    assert can_change_velocity.get_velocity() == Vector(-1, 0)
