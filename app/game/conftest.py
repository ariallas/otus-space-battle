import pytest

from app.core import ioc_scoped


@pytest.fixture(autouse=True)
def _setup_scoped_ioc() -> None:
    ioc_scoped.setup()
