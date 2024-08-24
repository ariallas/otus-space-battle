from pathlib import Path

from app.game.behaviour.fuel import IConsumesFuel
from app.game.behaviour.movement import ICanChangeVelocity, IMovable
from app.game.behaviour.rotation import IRotatable
from codegen import adapter

# ruff: noqa: F401


def main() -> None:
    interfaces = [IMovable, IConsumesFuel, ICanChangeVelocity, IRotatable]
    destination = Path("app/autogenerated")
    adapter.generate(interfaces, destination / "adapters")


if __name__ == "__main__":
    main()
