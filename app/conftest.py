import pytest

from app.core import ioc_scoped
from app.core.command import ICommand
from app.core.ioc import IoC


@pytest.fixture(autouse=True)
def _setup_scoped_ioc() -> None:
    ioc_scoped.setup()
    IoC[ICommand].resolve("IoC.Scope.Current.Clear").execute()
