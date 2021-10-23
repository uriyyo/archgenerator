from contextlib import contextmanager
from functools import wraps
from typing import Iterator

from selene.browser import set_driver
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager


def _create_headless_browser() -> Chrome:
    options = ChromeOptions()
    # options.headless = True  # TODO: investigate why it fails when running in a headless mode
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


def with_chrome(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with chrome():
            return func(*args, **kwargs)

    return wrapper


__all__ = ["chrome", "with_chrome"]
