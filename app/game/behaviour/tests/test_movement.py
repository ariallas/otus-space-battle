from typing import Any

import pytest

from app.core.command import CommandError
from app.core.ioc import IoC
from app.game.behaviour.movement import IMovable, MoveCommand, ioc_setup_imovable
from app.game.setup.adapters import ioc_setup_adapters
from app.game.uobject import UObject
from app.game.value_types import Vector
from tests.mocks import MockUObject


@pytest.fixture(autouse=True)
def _ioc_setup() -> None:
    ioc_setup_imovable()
    ioc_setup_adapters()


DIRS_NUMBER = 72


def make_movable_uobject(
    position: Vector, velocity: Vector, uobj: UObject | None = None
) -> UObject:
    if not uobj:
        uobj = MockUObject()
    uobj.set_property("movable_position", position)
    uobj.set_property("movable_angle", velocity.get_angle(DIRS_NUMBER))
    uobj.set_property("movable_abs_velocity", velocity.get_length())
    return uobj


def test_movement() -> None:
    uobj = make_movable_uobject(Vector(12, 5), Vector(-7, 3))

    movable = IoC[IMovable].resolve("Adapter", IMovable, uobj)
    move = MoveCommand(movable)
    move.execute()

    assert movable.get_position() == Vector(5, 8)


def test_get_movable_position_error() -> None:
    uobj = make_movable_uobject(Vector(12, 5), Vector(-7, 3))

    def get_property_side_effect(prop: str) -> Any:
        if prop == "movable_position":
            raise CommandError
        return original_get_property(prop)

    original_get_property = uobj.get_property
    uobj.get_property = get_property_side_effect

    with pytest.raises(Exception):
        MoveCommand(IoC[IMovable].resolve("Adapter", IMovable, uobj)).execute()


def test_get_movable_abs_velocity_error() -> None:
    uobj = make_movable_uobject(Vector(12, 5), Vector(-7, 3))

    def get_property_side_effect(prop: str) -> Any:
        if prop == "movable_abs_velocity":
            raise CommandError
        return original_get_property(prop)

    original_get_property = uobj.get_property
    uobj.get_property = get_property_side_effect

    with pytest.raises(Exception):
        MoveCommand(IoC[IMovable].resolve("Adapter", IMovable, uobj)).execute()


def test_movable_position_error() -> None:
    uobj = make_movable_uobject(Vector(12, 5), Vector(-7, 3))

    def set_property_side_effect(prop: str, value: Any) -> Any:
        if prop == "movable_position":
            raise CommandError
        return original_set_property(prop, value)

    original_set_property = uobj.set_property
    uobj.set_property = set_property_side_effect

    with pytest.raises(Exception):
        MoveCommand(IoC[IMovable].resolve("Adapter", IMovable, uobj)).execute()
