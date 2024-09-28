from abc import ABC, abstractmethod
from typing import Any, override


class UObject(ABC):
    @abstractmethod
    def get_property(self, prop: str) -> Any: ...

    @abstractmethod
    def set_property(self, prop: str, value: Any) -> None: ...


class UObjectImpl(UObject):
    def __init__(self) -> None:
        self._props: dict[str, Any] = {}

    @override
    def get_property(self, prop: str) -> Any:
        return self._props[prop]

    @override
    def set_property(self, prop: str, value: Any) -> None:
        self._props[prop] = value
