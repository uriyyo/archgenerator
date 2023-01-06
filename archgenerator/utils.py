from asyncio import sleep, to_thread
from functools import wraps
from itertools import count
from random import randint
from typing import Callable, TypeVar, Awaitable, Protocol, ParamSpec, cast, overload, Any, no_type_check

P = ParamSpec("P")
T = TypeVar("T")


@overload
def retry(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    pass


@overload
def retry(
    *,
    attempts: int = ...,
    delay_range: tuple[int, int] = ...,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    pass


@no_type_check
def retry(
    func: Any | None = None,
    /,
    *,
    attempts: int = 10,
    delay_range: tuple[int, int] = (1, 10),
) -> Any:
    if func is not None:
        return retry(
            attempts=attempts,
            delay_range=delay_range,
        )(func)

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


class CachedFunction(Protocol[P, T]):
    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        pass

    def add_provider(self, provider: Callable[P, T]) -> None:
        pass


def cached(func: Callable[P, Awaitable[T]]) -> CachedFunction[P, T]:
    providers: list[Callable[P, T]] = []

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        for provider in providers:
            try:
                return provider(*args, **kwargs)
            except LookupError:
                pass

        return await func(*args, **kwargs)

    wrapper.add_provider = providers.append  # type: ignore[attr-defined]
    return cast(CachedFunction[P, T], wrapper)


def run_in_executor(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await to_thread(func, *args, **kwargs)

    return wrapper


__all__ = [
    "cached",
    "retry",
    "run_in_executor",
]
