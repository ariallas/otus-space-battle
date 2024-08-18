from typing import override

from loguru import logger

from app.core.command import ICommand
from app.game.behaviour.movement import ICanChangeVelocity
from app.game.behaviour.rotation import IRotatable
from app.game.value_types import Vector


class AdjustVelocityToRotationCommand(ICommand):
    def __init__(self, rotatable: IRotatable, can_change_velocity: ICanChangeVelocity) -> None:
        self._rotatable = rotatable
        self._can_change_velocity = can_change_velocity

    @override
    def execute(self) -> None:
        target_angle = self._rotatable.get_angle()
        try:
            current_velocity = self._can_change_velocity.get_velocity()
        except Exception as e:
            logger.debug(f"Cannot adjust velocity for {self._can_change_velocity}: {e}")
            return
        length = current_velocity.get_length()

        new_velocity = Vector.from_angle_and_length(target_angle, length)
        logger.debug(
            f"Adjusting {self._can_change_velocity} velocity from {current_velocity} to {new_velocity}, "
            f"to match current angle of {target_angle}"
        )
        self._can_change_velocity.set_velocity(new_velocity)
