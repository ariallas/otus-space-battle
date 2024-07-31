from __future__ import annotations

import math
from typing import Self

from app.exceptions import AngleAdditionError

DEFAULT_DIRECTIONS_NUMBER = 72


class Vector:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    @classmethod
    def from_angle_and_length(cls, angle: Angle, length: float) -> Self:
        return cls(
            round(length * math.cos(angle.to_rads())),
            round(length * math.sin(angle.to_rads())),
        )

    def get_length(self) -> float:
        return math.sqrt(pow(self.x, 2) + pow(self.y, 2))

    def get_angle(self, directions_number: int = DEFAULT_DIRECTIONS_NUMBER) -> Angle:
        return Angle.from_rads(math.atan2(self.y, self.x), directions_number)

    def __add__(self, other: Vector) -> Vector:
        return Vector(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: Vector) -> Self:
        self.x += other.x
        self.y += other.y
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            raise NotImplementedError
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"Vector(x={self.x}, y={self.y})"


class Angle:
    def __init__(self, direction: int, directions_number: int = DEFAULT_DIRECTIONS_NUMBER) -> None:
        self._direction = direction
        self._directions_number = directions_number

    @classmethod
    def from_degrees(
        cls, degrees: float, directions_number: int = DEFAULT_DIRECTIONS_NUMBER
    ) -> Self:
        direction = round((degrees / 360) * directions_number) % directions_number
        return cls(direction, directions_number)

    @classmethod
    def from_rads(cls, rads: float, directions_number: int = DEFAULT_DIRECTIONS_NUMBER) -> Self:
        direction = round((rads / 2 / math.pi) * directions_number) % directions_number
        return cls(direction, directions_number)

    def to_degrees(self) -> float:
        return self._direction * (360 / self._directions_number)

    def to_rads(self) -> float:
        return self._direction * (2 * math.pi / self._directions_number)

    def _check_same_directions_number(self, other: Angle) -> None:
        if self._directions_number != other._directions_number:  # noqa: SLF001
            raise AngleAdditionError(
                f"Trying to add angles {self} and {other} with different direction numbers"
            )

    def __add__(self, other: Angle) -> Angle:
        self._check_same_directions_number(other)
        new_dir = (self._direction + other._direction) % self._directions_number
        return Angle(new_dir, self._directions_number)

    def __iadd__(self, other: Angle) -> Self:
        self._check_same_directions_number(other)
        self._direction = (self._direction + other._direction) % self._directions_number
        return self

    def __repr__(self) -> str:
        return (
            f"Angle(direction={self._direction}/{self._directions_number}, "
            f"degrees={self.to_degrees():.1f}, rad={self.to_rads():.3f})"
        )
