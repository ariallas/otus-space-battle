import threading
from contextvars import ContextVar
from typing import Any, Protocol

from app.core.ioc import IoC, ResolveStrategy


class IoCDependency(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class Scope:
    def __init__(self, name: str, store: dict[str, IoCDependency]) -> None:
        self.name = name
        self.store = store

    def __repr__(self) -> str:
        return f"Scope(name={self.name}, keys={list(self.store.keys())})"


class ScopedIoC:
    _current_scope: ContextVar[Scope | None] = ContextVar("_current_scope", default=None)

    def __init__(self) -> None:
        self._current_scope.set(None)
        self._root_scope = Scope("Root", {})

        self._setup_lock = threading.Lock()
        self._is_setup: bool = False

    def setup(self) -> None:
        with self._setup_lock:
            if self._is_setup:
                return

            self._root_scope.store["IoC.Scope.Current.Set"] = self._set_scope
            self._root_scope.store["IoC.Scope.Current.Clear"] = self._clear_scope
            self._root_scope.store["IoC.Scope.Current"] = self._get_current_scope
            self._root_scope.store["IoC.Scope.Parent"] = self._get_parent_scope
            self._root_scope.store["IoC.Scope.Create"] = self._create_scope
            self._root_scope.store["IoC.Scope.Register"] = self._register_dependency

            def update_ioc_strategy(_old_strategy: ResolveStrategy) -> ResolveStrategy:
                return self._resolve_strategy

            IoC.resolve("Update IoC Resolve Strategy")(update_ioc_strategy)

            self._is_setup = True

    def _set_scope(self, scope: Scope) -> None:
        self._current_scope.set(scope)

    def _clear_scope(self) -> None:
        self._current_scope.set(None)

    def _get_current_scope(self) -> Scope:
        return self._current_scope.get() or self._root_scope

    def _get_parent_scope(self) -> Scope:
        raise ScopedIoCError("Root scope has no parent scope")

    def _create_scope(self, name: str, parent: Scope | None = None) -> Scope:
        new_scope = Scope(name, {})
        if not parent:
            parent = self._get_current_scope()
        new_scope.store["IoC.Scope.Parent"] = lambda: parent
        return new_scope

    def _register_dependency(self, dependency: str, dependency_func: IoCDependency) -> None:
        self._get_current_scope().store[dependency] = dependency_func

    def _resolve_strategy(self, dependency: str, *args: Any, **kwargs: Any) -> Any:
        scope = self._get_current_scope()
        while True:
            if strategy := scope.store.get(dependency):
                return strategy(*args, **kwargs)
            scope = scope.store["IoC.Scope.Parent"]()


_scoped_ioc = ScopedIoC()
setup = _scoped_ioc.setup


class ScopedIoCError(Exception): ...
