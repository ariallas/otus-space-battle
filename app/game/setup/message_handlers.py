from queue import Queue

from loguru import logger

from app.core.command import ICommand, LambdaCommand
from app.core.ioc import IoC
from app.game.behaviour.movement import ICanChangeVelocity, IMovable, MoveCommand
from app.game.setup.behaviour import ioc_setup_icanchangevelocity, ioc_setup_imovable
from app.game.uobject import UObject, UObjectImpl
from app.game.value_types import Vector
from app.server import Message


def ioc_setup_move() -> None:
    ioc_setup_imovable()
    ioc_setup_icanchangevelocity()

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "MessageHandler.create_object",
        LambdaCommand(_handle_create_object).setup,
    ).execute()

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "MessageHandler.move",
        LambdaCommand(_handle_move).setup,
    ).execute()


def _handle_create_object(message: Message) -> None:
    logger.info("Handling 'create_object'")
    items = IoC[dict[int, UObject]].resolve("Game.items")

    items[message.object_id] = UObjectImpl()


def _handle_move(message: Message) -> None:
    logger.info("Handling 'move'")
    items = IoC[dict[int, UObject]].resolve("Game.items")
    queue = IoC[Queue[ICommand]].resolve("Game.Queue")

    obj = items[message.object_id]

    can_change_velocity = IoC[ICanChangeVelocity].resolve("Adapter", ICanChangeVelocity, obj)
    movable = IoC[IMovable].resolve("Adapter", IMovable, obj)

    args = message.args
    movable.set_position(Vector(args["x"], args["y"]))
    can_change_velocity.set_velocity(Vector(args["velocity_x"], args["velocity_y"]))

    queue.put(MoveCommand(movable))
