from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from unittest.mock import Mock

import pytest
from loguru import logger

from app.core.command import ICommand
from app.core.ioc import IoC, IoCResolveDependencyError
from app.core.ioc_scoped import Scope
from app.core.ioc_scoped import setup as scoped_ioc_setup


@pytest.fixture(autouse=True)
def _setup_scoped_ioc() -> None:
    scoped_ioc_setup()


@pytest.fixture(autouse=True)
def _clear_scope(_setup_scoped_ioc: Any) -> Iterator[None]:
    yield
    IoC[ICommand].resolve("IoC.Scope.Current.Clear").execute()


def test_ioc_scope_ops() -> None:
    root_scope = IoC[Scope].resolve("IoC.Scope.Current")
    assert isinstance(root_scope, Scope)
    logger.debug(f"Root scope: {root_scope}")

    new_scope = IoC[Scope].resolve("IoC.Scope.Create", "scope1")
    assert new_scope is not root_scope

    IoC[ICommand].resolve("IoC.Scope.Current.Set", new_scope).execute()
    assert IoC[Scope].resolve("IoC.Scope.Current") is new_scope

    assert IoC[Scope].resolve("IoC.Scope.Parent") is root_scope

    IoC[ICommand].resolve("IoC.Scope.Current.Clear").execute()
    assert IoC[Scope].resolve("IoC.Scope.Current") is root_scope


def test_root_parent_error() -> None:
    with pytest.raises(IoCResolveDependencyError):
        IoC[Scope].resolve("IoC.Scope.Parent")


def test_create_scope_with_parent() -> None:
    scope1 = IoC[Scope].resolve("IoC.Scope.Create", "scope1")
    scope2 = IoC[Scope].resolve("IoC.Scope.Create", "scope2", scope1)
    IoC[ICommand].resolve("IoC.Scope.Current.Set", scope2).execute()

    assert IoC[Scope].resolve("IoC.Scope.Current") is scope2
    assert IoC[Scope].resolve("IoC.Scope.Parent") is scope1


def test_resolve_error() -> None:
    with pytest.raises(IoCResolveDependencyError):
        IoC.resolve("Nonexistent Dependency")


MOCK_ARGS = [1, "a"]
MOCK_KWARGS = {"b": "c", "d": 5}


def test_resolve_from_root() -> None:
    mock = Mock()
    IoC[ICommand].resolve("IoC.Scope.Register", "mock", mock).execute()

    IoC.resolve("mock", *MOCK_ARGS, **MOCK_KWARGS)
    mock.assert_called_once_with(*MOCK_ARGS, **MOCK_KWARGS)


def test_resolve_from_current() -> None:
    scope1 = IoC[Scope].resolve("IoC.Scope.Create", "scope1")
    IoC[ICommand].resolve("IoC.Scope.Current.Set", scope1).execute()

    mock = Mock()
    IoC[ICommand].resolve("IoC.Scope.Register", "mock", mock).execute()

    IoC.resolve("mock", *MOCK_ARGS, **MOCK_KWARGS)
    mock.assert_called_once_with(*MOCK_ARGS, **MOCK_KWARGS)


def test_resolve_from_parent() -> None:
    scope1 = IoC[Scope].resolve("IoC.Scope.Create", "scope1")

    mock = Mock()
    IoC[ICommand].resolve("IoC.Scope.Register", "mock", mock).execute()

    scope2 = IoC[Scope].resolve("IoC.Scope.Create", "scope2", scope1)
    IoC[ICommand].resolve("IoC.Scope.Current.Set", scope2).execute()

    IoC.resolve("mock", *MOCK_ARGS, **MOCK_KWARGS)
    mock.assert_called_once_with(*MOCK_ARGS, **MOCK_KWARGS)


def test_multithreading_root_scope() -> None:
    root_scope = IoC[Scope].resolve("IoC.Scope.Current")

    def thread_func() -> None:
        scoped_ioc_setup()
        assert IoC[Scope].resolve("IoC.Scope.Current") is root_scope

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(thread_func)
        future.result()


def test_thread_local_scope() -> None:
    root_scope = IoC[Scope].resolve("IoC.Scope.Current")
    scope1 = IoC[Scope].resolve("IoC.Scope.Create", "scope1")
    IoC[ICommand].resolve("IoC.Scope.Current.Set", scope1).execute()

    def thread_func() -> None:
        assert IoC[Scope].resolve("IoC.Scope.Current") is root_scope

        scope2 = IoC[Scope].resolve("IoC.Scope.Create", "scope2")
        IoC[ICommand].resolve("IoC.Scope.Current.Set", scope2).execute()
        assert IoC[Scope].resolve("IoC.Scope.Current") is scope2

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(thread_func)
        future.result()

    assert IoC[Scope].resolve("IoC.Scope.Current") is scope1


def test_thread_local_resolve() -> None:
    def thread1_func() -> None:
        scope1 = IoC[Scope].resolve("IoC.Scope.Create", "scope1")
        IoC[ICommand].resolve("IoC.Scope.Current.Set", scope1).execute()

        mock1 = Mock()
        IoC[ICommand].resolve("IoC.Scope.Register", "mock", mock1).execute()
        IoC.resolve("mock", *MOCK_ARGS, **MOCK_KWARGS)
        mock1.assert_called_once_with(*MOCK_ARGS, **MOCK_KWARGS)

    def thread2_func() -> None:
        scope2 = IoC[Scope].resolve("IoC.Scope.Create", "scope2")
        IoC[ICommand].resolve("IoC.Scope.Current.Set", scope2).execute()

        mock2 = Mock()
        IoC[ICommand].resolve("IoC.Scope.Register", "mock", mock2).execute()
        IoC.resolve("mock", *MOCK_ARGS, **MOCK_KWARGS)
        mock2.assert_called_once_with(*MOCK_ARGS, **MOCK_KWARGS)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(thread1_func), executor.submit(thread2_func)]
        for future in futures:
            future.result()
