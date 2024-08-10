from app.command import ICommand
from app.ioc import InitScopedIoCCommand, Ioc, IocStrategyFunc
from app.movement import MoveCommand


def update_ioc_strategy(current_strategy: IocStrategyFunc) -> IocStrategyFunc:
    return current_strategy


def test_ioc() -> None:
    Ioc[ICommand].resolve("Update Ioc Strategy", update_ioc_strategy).execute()

    Ioc[ICommand].resolve("Ioc.unregister", "move").execute()
    Ioc[ICommand].resolve(
        "Ioc.register", "move", lambda args, kwargs: MoveCommand(*args, **kwargs)
    ).execute()
    Ioc[ICommand].resolve("Ioc.unregister", "move").execute()


def test_ioc_init() -> None:
    InitScopedIoCCommand().execute()
    print(Ioc.resolve("IoC.Scope.Current"))
