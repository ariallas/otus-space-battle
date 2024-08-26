from abc import ABCMeta
from typing import TypeVar

requested_adapter: list[ABCMeta] = []

T = TypeVar("T", bound=type)


def generate_adapter(cls: T) -> T:
    requested_adapter.append(cls)
    return cls
