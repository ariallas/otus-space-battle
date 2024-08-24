import re
from dataclasses import dataclass
from types import GenericAlias, UnionType
from typing import Any

import jinja2


def create_jinja_env() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader("codegen/templates"),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def camel2snake(camel: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel).lower()


@dataclass
class ParsedType:
    annotation: str
    dependencies: list[tuple[str, str]]


def parse_type(t: Any) -> ParsedType:
    if t is None or t is type(None):
        return ParsedType("None", [])
    if not isinstance(t, GenericAlias | UnionType):
        if t.__module__ == "builtins":
            return ParsedType(t.__qualname__, [])
        return ParsedType(t.__qualname__, [(t.__module__, t.__name__)])

    args = [parse_type(arg) for arg in t.__args__]

    dependencies: list[tuple[str, str]] = []
    for arg in args:
        dependencies.extend(arg.dependencies)

    if isinstance(t, UnionType):
        annotation = " | ".join(arg.annotation for arg in args)
    elif t.__qualname__ == "Callable":
        annotation = (
            f"Callable[[{', '.join(arg.annotation for arg in args[:-1])}], {args[-1].annotation}]"
        )
    else:
        annotation = f"{t.__qualname__}[{', '.join(arg.annotation for arg in args)}]"
    return ParsedType(annotation, dependencies)
