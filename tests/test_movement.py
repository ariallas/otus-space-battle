from typing import Any

import pytest

from app.exceptions import BaseSpaceBattleError
from app.game_object import UObject
from app.movement import MovableAdapter, MoveCommand
from app.value_types import Vector
from tests.mocks import MockUObject

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

    movable = MovableAdapter(uobj)
    move = MoveCommand(movable)
    move.execute()

    assert movable.get_position() == Vector(5, 8)


# Тесты на исключения очень уродливые, но я не понимаю
# как по-другому сделать, чтобы get_property/set_property выкидывали
# исключения только для конкретных значений параметров


def test_get_movable_position_error() -> None:
    uobj = make_movable_uobject(Vector(12, 5), Vector(-7, 3))

    def get_property_side_effect(prop: str) -> Any:
        if prop == "movable_position":
            raise BaseSpaceBattleError
        return original_get_property(prop)

    original_get_property = uobj.get_property
    uobj.get_property = get_property_side_effect

    with pytest.raises(BaseSpaceBattleError):
        MoveCommand(MovableAdapter(uobj)).execute()


def test_get_movable_abs_velocity_error() -> None:
    uobj = make_movable_uobject(Vector(12, 5), Vector(-7, 3))

    def get_property_side_effect(prop: str) -> Any:
        if prop == "movable_abs_velocity":
            raise BaseSpaceBattleError
        return original_get_property(prop)

    original_get_property = uobj.get_property
    uobj.get_property = get_property_side_effect

    with pytest.raises(BaseSpaceBattleError):
        MoveCommand(MovableAdapter(uobj)).execute()


def test_movable_position_error() -> None:
    uobj = make_movable_uobject(Vector(12, 5), Vector(-7, 3))

    def set_property_side_effect(prop: str, value: Any) -> Any:
        if prop == "movable_position":
            raise BaseSpaceBattleError
        return original_set_property(prop, value)

    original_set_property = uobj.set_property
    uobj.set_property = set_property_side_effect

    with pytest.raises(BaseSpaceBattleError):
        MoveCommand(MovableAdapter(uobj)).execute()
