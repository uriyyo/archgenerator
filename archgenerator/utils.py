from asyncio import sleep
from functools import wraps
from itertools import count
from random import randint
from typing import Tuple


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


__all__ = ["cached", "retry"]
