from collections.abc import Callable
from typing import Any, ClassVar, Protocol, override

from loguru import logger

from app.command import ICommand

# TODO resolve_strategy or strategy or ResolveDependency?

## Default IoC ##


class IocStrategyFunc(Protocol):
    def __call__(self, dependency: str, *args: Any, **kwargs: Any) -> Any: ...


def _default_ioc_strategy(dependency: str, *args: Any, **_kwargs: Any) -> Any:
    if dependency == "Update Ioc Strategy":
        return UpdateIocStrategyCommand(args[0])
    raise ValueError(f"Dependency '{dependency}' not found")


class Ioc[T]:
    strategy: IocStrategyFunc = _default_ioc_strategy

    @classmethod
    def resolve(cls, dependecy: str, *args: Any, **kwargs: Any) -> T:
        return cls.strategy(dependecy, *args, **kwargs)


## Updating IoC ##


class UpdateIocStrategyCommand(ICommand):
    def __init__(
        self,
        update_ioc_strategy: Callable[[IocStrategyFunc], IocStrategyFunc],
    ) -> None:
        self._update_ioc_strategy = update_ioc_strategy

    @override
    def execute(self) -> None:
        new_strategy = self._update_ioc_strategy(Ioc.strategy)
        logger.info(
            f"Updating IoC strategy from {Ioc.strategy.__qualname__} to {new_strategy.__qualname__}"
        )
        Ioc.strategy = new_strategy


## Scoped IoC ##


class IocDependency(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


Scope = dict[str, IocDependency]


class DependencyResolver:
    def __init__(self, scope: Scope) -> None:
        self._scope = scope

    def resolve(self, dependecy: str, *args: Any, **kwargs: Any) -> Any:
        scope = self._scope

        while True:
            if strategy := scope.get(dependecy):
                return strategy(*args, **kwargs)
            scope = self._scope["IoC.Scope.Parent"]()


class RegisterDependencyCommand(ICommand):
    def __init__(self, dependency: str, strategy: IocDependency) -> None:
        self._dependency = dependency
        self._strategy = strategy

    @override
    def execute(self) -> None:
        scope = Ioc[Scope].resolve("IoC.Scope.Current")
        scope[self._dependency] = self._strategy


class InitScopedIoCCommand(ICommand):
    # TODO Thread local
    current_scope: Scope | None = None
    root_scope: ClassVar[Scope] = {}

    @override
    def execute(self) -> None:
        def set_scope(scope: Scope) -> None:
            self.current_scope = scope

        def clear_scope() -> None:
            self.current_scope = None

        def current_scope() -> Scope:
            return self.current_scope or self.root_scope

        def parent_scope() -> Scope:
            raise Exception("Root scope has no parent scope")  # noqa: TRY002

        def create_scope(parent: Scope | None = None) -> Scope:
            new_scope: Scope = {}
            if not parent:
                parent = current_scope()
            new_scope["IoC.Scope.Parent"] = lambda: parent
            return new_scope

        def register_dependency(dependency: str, strategy: IocDependency) -> None:
            # TODO is this right??
            # scope = Ioc[Scope].resolve("IoC.Scope.Current")
            current_scope()[dependency] = strategy

        self.root_scope["IoC.Scope.Current.Set"] = set_scope
        self.root_scope["IoC.Scope.Current.Clear"] = clear_scope
        self.root_scope["IoC.Scope.Current"] = current_scope
        self.root_scope["IoC.Scope.Parent"] = parent_scope
        self.root_scope["IoC.Scope.Create"] = create_scope
        self.root_scope["IoC.Scope.Register"] = register_dependency

        def update_ioc_strategy(_current_strategy: IocStrategyFunc) -> IocStrategyFunc:
            def _resolve(dependency: str, *args: Any, **kwargs: Any) -> Any:
                resolver = DependencyResolver(current_scope())
                return resolver.resolve(dependency, *args, **kwargs)

            return _resolve

        Ioc[ICommand].resolve("Update Ioc Strategy", update_ioc_strategy).execute()
