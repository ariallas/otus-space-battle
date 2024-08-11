from collections.abc import Callable, MutableMapping
from typing import Any, Protocol

from loguru import logger

# TODO Exceptions

## Default IoC ##


class ResolveStrategyFunc(Protocol):
    def __call__(self, dependency: str, *args: Any, **kwargs: Any) -> Any: ...


def _default_ioc_resolve_strategy(dependency: str, *_args: Any, **_kwargs: Any) -> Any:
    if dependency == "Update IoC Resolve Strategy":
        return _update_ioc_resolve_strategy
    raise ValueError(f"Dependency '{dependency}' not found")


def _update_ioc_resolve_strategy(
    strategy_updater: Callable[[ResolveStrategyFunc], ResolveStrategyFunc],
) -> None:
    new_strategy = strategy_updater(IoC.resolve_strategy)
    logger.info(
        f"Updating IoC strategy from '{IoC.resolve_strategy.__qualname__}' to '{new_strategy.__qualname__}'"
    )
    IoC.resolve_strategy = new_strategy


class IoC[T]:
    resolve_strategy: ResolveStrategyFunc = _default_ioc_resolve_strategy

    @classmethod
    def resolve(cls, dependency: str, *args: Any, **kwargs: Any) -> T:
        return cls.resolve_strategy(dependency, *args, **kwargs)


## Scoped IoC ##


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

        def update_ioc_strategy(_current_strategy: ResolveStrategyFunc) -> ResolveStrategyFunc:
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
        raise Exception("Root scope has no parent scope")  # noqa: TRY002

    def _create_scope(self, parent: Scope | None = None) -> Scope:
        new_scope: Scope = {}
        if not parent:
            parent = self._get_current_scope()
        new_scope["IoC.Scope.Parent"] = lambda: parent
        return new_scope

    def _register_dependency(self, dependency: str, strategy: IoCDependency) -> None:
        self._get_current_scope()[dependency] = strategy

    def _resolve_strategy(self, dependency: str, *args: Any, **kwargs: Any) -> Any:
        scope = self._get_current_scope()
        while True:
            if strategy := scope.get(dependency):
                return strategy(*args, **kwargs)
            scope = scope["IoC.Scope.Parent"]()


scoped_ioc = ScopedIoC()
