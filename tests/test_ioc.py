from app.command import ICommand
from app.core import ioc_scoped
from app.core.ioc import IoC, ResolveStrategyFunc
from app.movement import MoveCommand


def update_ioc_strategy(current_strategy: ResolveStrategyFunc) -> ResolveStrategyFunc:
    return current_strategy


def test_ioc() -> None:
    IoC.resolve("Update IoC Resolve Strategy")(update_ioc_strategy)

    IoC[ICommand].resolve("Ioc.unregister", "move").execute()
    IoC[ICommand].resolve(
        "Ioc.register", "move", lambda args, kwargs: MoveCommand(*args, **kwargs)
    ).execute()
    IoC[ICommand].resolve("Ioc.unregister", "move").execute()


def test_ioc_init() -> None:
    ioc_scoped.setup()
    print(IoC.resolve("IoC.Scope.Current"))
