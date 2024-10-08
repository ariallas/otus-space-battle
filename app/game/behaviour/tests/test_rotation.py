from typing import Any

import pytest

from app.core.command import CommandError
from app.core.ioc import IoC
from app.game.behaviour.rotation import IRotatable, RotateCommand
from app.game.setup.adapters import ioc_setup_adapters
from app.game.setup.behaviour import ioc_setup_irotatable
from app.game.uobject import UObject
from app.game.value_types import Angle
from tests.mocks import MockUObject


@pytest.fixture(autouse=True)
def _ioc_setup() -> None:
    ioc_setup_irotatable()
    ioc_setup_adapters()


DIRS_NUMBER = 72


def make_rotatable_uobject(
    angle: Angle, angular_velocity: Angle, uobj: UObject | None = None
) -> UObject:
    if not uobj:
        uobj = MockUObject()
    uobj.set_property("rotatable_angle", angle)
    uobj.set_property("rotatable_angular_velocity", angular_velocity)
    return uobj


def test_rotation() -> None:
    uobj = make_rotatable_uobject(
        angle=Angle.from_degrees(45, DIRS_NUMBER),
        angular_velocity=Angle.from_degrees(180, DIRS_NUMBER),
    )

    rotatable = IoC[IRotatable].resolve("Adapter", IRotatable, uobj)
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
            raise CommandError
        return original_get_property(prop)

    original_get_property = uobj.get_property
    uobj.get_property = get_property_side_effect

    with pytest.raises(Exception):
        RotateCommand(IoC[IRotatable].resolve("Adapter", IRotatable, uobj)).execute()


def test_set_rotatable_angle_error() -> None:
    uobj = make_rotatable_uobject(
        Angle.from_degrees(45, DIRS_NUMBER),
        Angle.from_degrees(180, DIRS_NUMBER),
    )

    def set_property_side_effect(prop: str, value: Any) -> Any:
        if prop == "rotatable_angle":
            raise CommandError
        return original_get_property(prop, value)

    original_get_property = uobj.set_property
    uobj.set_property = set_property_side_effect

    with pytest.raises(Exception):
        RotateCommand(IoC[IRotatable].resolve("Adapter", IRotatable, uobj)).execute()
