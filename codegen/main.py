import jinja2

from app.game.behaviour import movement

imovable = movement.IMovable

# ruff: noqa


def main() -> None:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("codegen/templates"),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("adapter.py.j2")


if __name__ == "__main__":
    main()
