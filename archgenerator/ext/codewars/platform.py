from asyncio import gather
from typing import List

import click
from httpx import AsyncClient

from .config import CONFIG
from .context import CODEWARS_PASSWORD, CODEWARS_EMAIL
from .fetcher import sign_in, katas_stream, kata_description, get_kata_description
from ...models import Book
from ...platform import Platform, TaskLike


class CodeWarsPlatform(Platform):
    name = "codewars"
    config = CONFIG
    section_reversed = True

    options = {
        "email": (
            click.option("--email", envvar="CODEWARS_EMAIL", type=str, required=True),
            CODEWARS_EMAIL,
        ),
        "password": (
            click.option(
                "--password", envvar="CODEWARS_PASSWORD", type=str, required=True
            ),
            CODEWARS_PASSWORD,
        ),
    }

    def init_cache(self, book: Book):
        tasks = [task for section in book.sections for task in section.tasks]

        descriptions_map = {
            task.metadata["description"]: task.description for task in tasks
        }

        get_kata_description.add_provider(
            lambda client, kata: descriptions_map[kata.href]
        )

    async def fetch(self) -> List[TaskLike]:
        async with AsyncClient(
            base_url="https://www.codewars.com", timeout=30
        ) as client:
            await sign_in(client)

            katas = [kata async for kata in katas_stream(client)]
            await gather(*(kata_description(client, kata) for kata in katas))

            return katas


__all__ = ["CodeWarsPlatform"]
