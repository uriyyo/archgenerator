from contextlib import contextmanager
from functools import wraps
from typing import Iterator, TypeVar, ParamSpec, Callable

from selene.browser import set_driver
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager


def _create_headless_browser() -> Chrome:
    options = ChromeOptions()
    options.headless = True
    driver = Chrome(ChromeDriverManager().install(), options=options)

    return driver


@contextmanager
def chrome() -> Iterator[Chrome]:
    driver = _create_headless_browser()
    set_driver(driver)

    try:
        yield driver
    finally:
        driver.quit()


T = TypeVar("T")
P = ParamSpec("P")


def with_chrome(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with chrome():
            return func(*args, **kwargs)

    return wrapper


__all__ = [
    "chrome",
    "with_chrome",
]
