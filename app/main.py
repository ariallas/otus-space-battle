from app.core import ioc_scoped
from app.game.setup.adapters import ioc_setup_adapters
from app.game.setup.state import ioc_setup_game_state

# from app.game.value_types import Vector


def main() -> None:
    # v = Vector(-7, 3)

    # a = v.get_angle()
    # ln = v.get_length()

    # print(a)
    # print(ln)

    # vv = Vector.from_angle_and_length(a, ln)
    # print(vv)
    # print(vv.get_angle())

    # v = Vector(-3, 7)
    # # v = Vector(1, 1)
    # print(v)
    # print(v.get_length())
    # print(v.get_angle())

    ioc_scoped.setup()
    ioc_setup_adapters()
    ioc_setup_game_state()


if __name__ == "__main__":
    main()
