from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Self, override

from app.exceptions import CommandError


class ICommand(ABC):
    @abstractmethod
    def execute(self) -> None: ...


class MacroCommand(ICommand):
    def __init__(self, commands: list[ICommand]) -> None:
        self._commands = commands

    @override
    def execute(self) -> None:
        for command in self._commands:
            try:
                command.execute()
            except Exception as exc:
                raise CommandError(f"Error while executing MacroCommand: {exc}") from exc


class LambdaCommand(ICommand):
    def __init__(self, func: Callable) -> None:
        self._func = func

    def set_args(self, *args: Any, **kwargs: Any) -> Self:
        self._args = args
        self._kwargs = kwargs
        return self

    @override
    def execute(self) -> None:
        self._func(*self._args, **self._kwargs)
