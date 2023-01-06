from asyncio import gather

import click
from httpx import AsyncClient
from more_itertools import chunked

from .config import CONFIG
from .context import CODEWARS_PASSWORD, CODEWARS_EMAIL
from .fetcher import sign_in, katas_stream, kata_description, get_kata_description
from ...consts import TASKS_CHUNK_SIZE
from ...models import Book
from ...platform import Platform, TaskLike


class CodeWarsPlatform(Platform):
    name = "codewars"
    config = CONFIG
    section_reversed = True

    options = {
        "email": (
            click.option("--email", envvar="CODEWARS_EMAIL", type=str),
            CODEWARS_EMAIL,
        ),
        "password": (
            click.option("--password", envvar="CODEWARS_PASSWORD", type=str),
            CODEWARS_PASSWORD,
        ),
    }

    def init_cache(self, book: Book) -> None:
        tasks = [task for section in book.sections for task in section.tasks]

        descriptions_map: dict[str, str] = {
            task.metadata["description"]: task.description for task in tasks if task.description
        }

        get_kata_description.add_provider(lambda client, kata: descriptions_map[kata.href])

    async def fetch(self) -> list[TaskLike]:
        async with AsyncClient(
            base_url="https://www.codewars.com",
            timeout=30,
            follow_redirects=True,
        ) as client:
            await sign_in(client)

            katas = [kata async for kata in katas_stream(client)]

            for chunk in chunked(katas, TASKS_CHUNK_SIZE):
                await gather(*(kata_description(client, kata) for kata in chunk))

            return katas


__all__ = [
    "CodeWarsPlatform",
]
