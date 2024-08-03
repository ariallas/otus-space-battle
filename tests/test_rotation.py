from typing import Any

import pytest

from app.exceptions import BaseSpaceBattleError
from app.game_object import UObject
from app.rotation import RotatableAdapter, RotateCommand
from app.value_types import Angle
from tests.mocks import MockUObject

DIRS_NUMBER = 72


def make_rotatable_uobject(angle: Angle, angular_velocity: Angle) -> UObject:
    uobj = MockUObject()
    uobj.set_property("rotatable_angle", angle)
    uobj.set_property("rotatable_angular_velocity", angular_velocity)
    return uobj


def test_rotation() -> None:
    uobj = make_rotatable_uobject(
        angle=Angle.from_degrees(45, DIRS_NUMBER),
        angular_velocity=Angle.from_degrees(180, DIRS_NUMBER),
    )

    rotatable = RotatableAdapter(uobj)
    rotate = RotateCommand(rotatable)

    rotate.execute()
    assert rotatable.get_angle().to_degrees() == 225

    rotate.execute()
    assert rotatable.get_angle().to_degrees() == 45


def test_get_rotatable_angle_error() -> None:
    uobj = make_rotatable_uobject(
        Angle.from_degrees(45, DIRS_NUMBER),
        Angle.from_degrees(180, DIRS_NUMBER),
    )

    def get_property_side_effect(prop: str) -> Any:
        if prop == "rotatable_angle":
            raise BaseSpaceBattleError
        return original_get_property(prop)

    original_get_property = uobj.get_property
    uobj.get_property = get_property_side_effect

    with pytest.raises(BaseSpaceBattleError):
        RotateCommand(RotatableAdapter(uobj)).execute()


def test_set_rotatable_angle_error() -> None:
    uobj = make_rotatable_uobject(
        Angle.from_degrees(45, DIRS_NUMBER),
        Angle.from_degrees(180, DIRS_NUMBER),
    )

    def set_property_side_effect(prop: str, value: Any) -> Any:
        if prop == "rotatable_angle":
            raise BaseSpaceBattleError
        return original_get_property(prop, value)

    original_get_property = uobj.set_property
    uobj.set_property = set_property_side_effect

    with pytest.raises(BaseSpaceBattleError):
        RotateCommand(RotatableAdapter(uobj)).execute()
