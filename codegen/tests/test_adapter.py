from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from app.core.command import ICommand
from app.core.ioc import IoC
from app.game.uobject import UObject
from app.game.value_types import Vector
from codegen.adapter import template_adapter

GETTER_ADAPTER = f"""
from typing import override

from {ICommand.__module__} import ICommand
from {IoC.__module__} import IoC
from {UObject.__module__} import UObject
from {Vector.__module__} import Vector
from {__name__} import ITestGetter


class TestGetterAdapter(ITestGetter):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def get_something(self) -> Vector | int | None:
        return IoC[Vector | int | None].resolve(
            "ITestGetter.something.Get",
            self._uobject,
        )
""".strip()


def test_getter() -> None:
    class ITestGetter(ABC):
        @abstractmethod
        def get_something(self) -> Vector | int | None: ...

    filename, content = template_adapter(ITestGetter)
    assert filename == "test_getter_adapter.py"
    assert content.strip() == GETTER_ADAPTER


SETTER_ADAPTER = f"""
from typing import override

from {ICommand.__module__} import ICommand
from {IoC.__module__} import IoC
from {UObject.__module__} import UObject
from {Vector.__module__} import Vector
from {__name__} import ITestSetter


class TestSetterAdapter(ITestSetter):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def set_something(self, value: list[Vector]) -> None:
        IoC[ICommand].resolve(
            "ITestSetter.something.Set",
            self._uobject,
            value,
        ).execute()
""".strip()


def test_setter() -> None:
    class ITestSetter(ABC):
        @abstractmethod
        def set_something(self, value: list[Vector]) -> None: ...

    filename, content = template_adapter(ITestSetter)
    assert filename == "test_setter_adapter.py"
    assert content.strip() == SETTER_ADAPTER


ARBITRARY_ADAPTER = f"""
from typing import override

from {ICommand.__module__} import ICommand
from {IoC.__module__} import IoC
from {UObject.__module__} import UObject
from {Vector.__module__} import Vector
from {__name__} import IArbitraryMethods


class ArbitraryMethodsAdapter(IArbitraryMethods):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def finish(
        self,
    ) -> None:
        IoC[ICommand].resolve(
            "IArbitraryMethods.finish",
            self._uobject,
        ).execute()

    @override
    def calculate_something(
        self,
        vec: Vector,
        aa: int,
    ) -> list[float]:
        return IoC[list[float]].resolve(
            "IArbitraryMethods.calculate_something",
            self._uobject,
            vec,
            aa,
        )
""".strip()


def test_arbitrary() -> None:
    """
    Для произвольных методов из IoC резолвится:
    - команда, если метод возвращает None
    - значение, если у метода есть возвращаемое значение
    """

    class IArbitraryMethods(ABC):
        @abstractmethod
        def finish(self) -> None: ...

        @abstractmethod
        def calculate_something(self, vec: Vector, aa: int) -> list[float]: ...

    filename, content = template_adapter(IArbitraryMethods)
    assert filename == "arbitrary_methods_adapter.py"
    assert content.strip() == ARBITRARY_ADAPTER


BIG_INTERFACE_ADAPTER = f"""
from typing import override

from {ICommand.__module__} import ICommand
from {IoC.__module__} import IoC
from {UObject.__module__} import UObject
from {Vector.__module__} import Vector
from {__name__} import IBigInterface
from typing import Any


class BigInterfaceAdapter(IBigInterface):
    def __init__(self, uobject: UObject) -> None:
        self._uobject = uobject

    @override
    def get_something(self) -> Vector:
        return IoC[Vector].resolve(
            "IBigInterface.something.Get",
            self._uobject,
        )

    @override
    def get_something_else(self) -> int:
        return IoC[int].resolve(
            "IBigInterface.something_else.Get",
            self._uobject,
        )

    @override
    def set_something(self, value: Vector) -> None:
        IoC[ICommand].resolve(
            "IBigInterface.something.Set",
            self._uobject,
            value,
        ).execute()

    @override
    def finish(
        self,
    ) -> None:
        IoC[ICommand].resolve(
            "IBigInterface.finish",
            self._uobject,
        ).execute()

    @override
    def calculate_something(
        self,
        vec: Vector,
        aa: Callable[[int, dict[str, Any]], Vector],
    ) -> list[float]:
        return IoC[list[float]].resolve(
            "IBigInterface.calculate_something",
            self._uobject,
            vec,
            aa,
        )
""".strip()


def test_everything_together() -> None:
    class IBigInterface(ABC):
        @abstractmethod
        def get_something(self) -> Vector: ...

        @abstractmethod
        def get_something_else(self) -> int: ...

        @abstractmethod
        def set_something(self, value: Vector) -> None: ...

        @abstractmethod
        def finish(self) -> None: ...

        @abstractmethod
        def calculate_something(
            self, vec: Vector, aa: Callable[[int, dict[str, Any]], Vector]
        ) -> list[float]: ...

    filename, content = template_adapter(IBigInterface)
    assert filename == "big_interface_adapter.py"
    assert content.strip() == BIG_INTERFACE_ADAPTER
