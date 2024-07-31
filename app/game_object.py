from abc import ABC, abstractmethod
from typing import Any


class UObject(ABC):
    @abstractmethod
    def get_property(self, prop: str) -> Any: ...

    @abstractmethod
    def set_property(self, prop: str, value: Any) -> None: ...
