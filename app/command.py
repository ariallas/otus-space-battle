from abc import ABC, abstractmethod
from typing import override

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
