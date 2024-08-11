from collections.abc import MutableMapping
from typing import Any, Protocol

from app.core.ioc import IoC, ResolveStrategyFunc


class IoCDependency(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


Scope = MutableMapping[str, IoCDependency]


class ScopedIoC:
    def __init__(self) -> None:
        # TODO Thread local
        self._current_scope: Scope | None = None
        self._root_scope: Scope = {}

        self._is_setup: bool = False

    def setup(self) -> None:
        if self._is_setup:
            return

        self._root_scope["IoC.Scope.Current.Set"] = self._set_scope
        self._root_scope["IoC.Scope.Current.Clear"] = self._clear_scope
        self._root_scope["IoC.Scope.Current"] = self._get_current_scope
        self._root_scope["IoC.Scope.Parent"] = self._get_parent_scope
        self._root_scope["IoC.Scope.Create"] = self._create_scope
        self._root_scope["IoC.Scope.Register"] = self._register_dependency

        def update_ioc_strategy(_old_strategy: ResolveStrategyFunc) -> ResolveStrategyFunc:
            return self._resolve_strategy

        IoC.resolve("Update IoC Resolve Strategy")(update_ioc_strategy)

        self._is_setup = True

    def _set_scope(self, scope: Scope) -> None:
        self._current_scope = scope

    def _clear_scope(self) -> None:
        self._current_scope = None

    def _get_current_scope(self) -> Scope:
        return self._current_scope or self._root_scope

    def _get_parent_scope(self) -> Scope:
        raise ScopedIoCError("Root scope has no parent scope")

    def _create_scope(self, parent: Scope | None = None) -> Scope:
        new_scope: Scope = {}
        if not parent:
            parent = self._get_current_scope()
        new_scope["IoC.Scope.Parent"] = lambda: parent
        return new_scope

    def _register_dependency(self, dependency: str, dependency_func: IoCDependency) -> None:
        self._get_current_scope()[dependency] = dependency_func

    def _resolve_strategy(self, dependency: str, *args: Any, **kwargs: Any) -> Any:
        scope = self._get_current_scope()
        while True:
            if strategy := scope.get(dependency):
                return strategy(*args, **kwargs)
            scope = scope["IoC.Scope.Parent"]()


_scoped_ioc = ScopedIoC()
setup = _scoped_ioc.setup


class ScopedIoCError(Exception): ...
