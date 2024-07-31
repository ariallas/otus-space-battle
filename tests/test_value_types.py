import pytest

from app.exceptions import AngleAdditionError
from app.value_types import Angle, Vector


def test_vector_add() -> None:
    v = Vector(2, 1) + Vector(3, 5)
    assert v.x == 5
    assert v.y == 6

    v += Vector(1, 1)
    assert v.x == 6
    assert v.y == 7


DIRS_NUMBER = 72


def test_vector_from_angle() -> None:
    assert Vector.from_angle_and_length(Angle.from_degrees(0, DIRS_NUMBER), 5) == Vector(5, 0)
    assert Vector.from_angle_and_length(Angle.from_degrees(90, DIRS_NUMBER), 5) == Vector(0, 5)
    assert Vector.from_angle_and_length(Angle.from_degrees(180, DIRS_NUMBER), 5) == Vector(-5, 0)
    assert Vector.from_angle_and_length(Angle.from_degrees(270, DIRS_NUMBER), 5) == Vector(0, -5)


def test_angle() -> None:
    assert Angle.from_degrees(45, DIRS_NUMBER).to_degrees() == 45

    assert Angle.from_degrees(47, DIRS_NUMBER).to_degrees() == 45
    assert Angle.from_degrees(48, DIRS_NUMBER).to_degrees() == 50

    assert Angle.from_degrees(360 + 45, DIRS_NUMBER).to_degrees() == 45

    assert (
        Angle.from_degrees(45, DIRS_NUMBER) + Angle.from_degrees(90, DIRS_NUMBER)
    ).to_degrees() == 135
    assert (
        Angle.from_degrees(225, DIRS_NUMBER) + Angle.from_degrees(180, DIRS_NUMBER)
    ).to_degrees() == 45


def test_angle_different_directions_number() -> None:
    with pytest.raises(AngleAdditionError):
        Angle(1, 2) + Angle(1, 3)  # pyright: ignore[reportUnusedExpression]
