from collections.abc import Callable
from typing import Any, Protocol

from loguru import logger


class ResolveStrategyFunc(Protocol):
    def __call__(self, dependency: str, *args: Any, **kwargs: Any) -> Any: ...


def _default_ioc_resolve_strategy(dependency: str, *_args: Any, **_kwargs: Any) -> Any:
    if dependency == "Update IoC Resolve Strategy":
        return _update_ioc_resolve_strategy
    raise IoCDependencyNotFoundError(dependency)


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


class IoCDependencyNotFoundError(Exception):
    def __init__(self, dependency: str) -> None:
        super().__init__(f"Dependency '{dependency}' not found")
