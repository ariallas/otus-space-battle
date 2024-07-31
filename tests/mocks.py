from typing import Any, override

from app.game_object import UObject


class MockUObject(UObject):
    def __init__(self) -> None:
        self._props: dict[str, Any] = {}

    @override
    def get_property(self, prop: str) -> Any:
        return self._props[prop]

    @override
    def set_property(self, prop: str, value: Any) -> None:
        self._props[prop] = value

    def __repr__(self) -> str:
        return f"MockUObject({self._props})"
