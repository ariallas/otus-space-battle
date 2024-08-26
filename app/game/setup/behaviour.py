from app.core.command import ICommand, LambdaCommand
from app.core.ioc import IoC
from app.game.uobject import UObject
from app.game.value_types import Angle, Vector


def ioc_setup_iconsumesfuel() -> None:
    def _get_amount(uobj: UObject) -> int:
        return uobj.get_property("fuel_amount")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IConsumesFuel.amount.Get",
        _get_amount,
    ).execute()

    def _set_amount(uobj: UObject, fuel_amount: int) -> None:
        uobj.set_property("fuel_amount", fuel_amount)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IConsumesFuel.amount.Set",
        LambdaCommand(_set_amount).setup,
    ).execute()

    def _get_consumption(uobj: UObject) -> int:
        return uobj.get_property("fuel_consumption")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IConsumesFuel.consumption.Get",
        _get_consumption,
    ).execute()


def ioc_setup_imovable() -> None:
    def _get_position(uobj: UObject) -> Vector:
        return uobj.get_property("movable_position")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IMovable.position.Get",
        _get_position,
    ).execute()

    def _set_position(uobj: UObject, v: Vector) -> None:
        uobj.set_property("movable_position", v)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IMovable.position.Set",
        LambdaCommand(_set_position).setup,
    ).execute()

    def _get_velocity(uobj: UObject) -> Vector:
        angle: Angle = uobj.get_property("movable_angle")
        velocity: int = uobj.get_property("movable_abs_velocity")
        return Vector.from_angle_and_length(angle, velocity)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IMovable.velocity.Get",
        _get_velocity,
    ).execute()


def ioc_setup_icanchangevelocity() -> None:
    def _get_velocity(uobj: UObject) -> Vector:
        angle: Angle = uobj.get_property("movable_angle")
        velocity: int = uobj.get_property("movable_abs_velocity")
        return Vector.from_angle_and_length(angle, velocity)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "ICanChangeVelocity.velocity.Get",
        _get_velocity,
    ).execute()

    def _set_velocity(uobj: UObject, v: Vector) -> None:
        angle = v.get_angle()
        length = v.get_length()
        uobj.set_property("movable_angle", angle)
        uobj.set_property("movable_abs_velocity", length)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "ICanChangeVelocity.velocity.Set",
        LambdaCommand(_set_velocity).setup,
    ).execute()


def ioc_setup_irotatable() -> None:
    def _get_angle(uobj: UObject) -> Angle:
        return uobj.get_property("rotatable_angle")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IRotatable.angle.Get",
        _get_angle,
    ).execute()

    def _set_angle(uobj: UObject, a: Angle) -> None:
        uobj.set_property("rotatable_angle", a)

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IRotatable.angle.Set",
        LambdaCommand(_set_angle).setup,
    ).execute()

    def _get_angular_velocity(uobj: UObject) -> Angle:
        return uobj.get_property("rotatable_angular_velocity")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "IRotatable.angular_velocity.Get",
        _get_angular_velocity,
    ).execute()
