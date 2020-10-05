from asyncio.tasks import gather
from typing import List, Any

import click
from httpx import AsyncClient
from more_itertools import chunked

from .config import CONFIG, DIFFICULTY_LEVEL
from .context import LEETCODE_SESSION
from .fetcher import (
    questions_list,
    fetch_solutions,
    fetch_descriptions,
    get_description,
    get_submission_code,
)
from ...models import Book
from ...platform import Platform, TaskLike

CHUNK_SIZE = 10


class LeetCodePlatform(Platform):
    name = "leetcode"
    config = CONFIG
    section_reversed = False

    options = {
        "session_id": (
            click.option(
                "--session-id", envvar="LEETCODE_SESSION_ID", type=str, required=False
            ),
            LEETCODE_SESSION,
        )
    }

    def init_cache(self, book: Book):
        tasks = [task for section in book.sections for task in section.tasks]

        descriptions_map = {task.metadata["slug"]: task.description for task in tasks}

        get_description.add_provider(
            lambda client, question: descriptions_map[question.slug]
        )

        submissions_map = {
            (submission_id, language): task.solutions[language][0].code
            for task in tasks
            for language, submission_id in task.metadata["submissions"].items()
        }

        get_submission_code.add_provider(
            lambda client, submission: submissions_map[
                (submission.id, submission.language)
            ]
        )

    def section_sorter_key(self, name: str) -> Any:
        return DIFFICULTY_LEVEL.index(name)

    async def fetch(self) -> List[TaskLike]:
        async with AsyncClient(
            base_url="https://leetcode.com",
            cookies={"LEETCODE_SESSION": LEETCODE_SESSION.get()},
        ) as client:
            questions = await questions_list(client)

            for chunk in chunked(questions, CHUNK_SIZE):
                await gather(*(fetch_solutions(client, question) for question in chunk))
                await gather(
                    *(fetch_descriptions(client, question) for question in chunk)
                )

            return questions


__all__ = ["LeetCodePlatform"]
