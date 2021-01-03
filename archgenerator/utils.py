from asyncio import sleep, get_event_loop
from contextvars import copy_context
from functools import wraps, partial
from itertools import count
from random import randint
from typing import Tuple, Callable, TypeVar, Awaitable

T = TypeVar("T")


def retry(attempts: int = 10, delay_range: Tuple[int, int] = (1, 10)):
    if callable(attempts):
        return retry()(attempts)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for i in count(1):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    if i == attempts:
                        raise

                    await sleep(randint(*delay_range))

        return wrapper

    return decorator


def cached(func):
    providers = []

    @wraps(func)
    async def wrapper(*args, **kwargs):
        for provider in providers:
            try:
                return provider(*args, **kwargs)
            except LookupError:
                pass

        return await func(*args, **kwargs)

    wrapper.add_provider = providers.append
    return wrapper


def run_in_executor(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        context = copy_context()

        return await get_event_loop().run_in_executor(
            None, partial(context.run, func, *args, **kwargs)
        )

    return wrapper


__all__ = ["cached", "retry", "run_in_executor"]
