from asyncio import gather
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Optional

from httpx import AsyncClient
from more_itertools import chunked

from .context import LEETCODE_SESSION
from ..models import Book
from ..scrapper import Page, one
from ..utils import retry, cached

CHUNK_SIZE = 10

DIFFICULTY_LEVEL = (None, "easy", "medium", "hard")
LANG_TO_NORMALIZE_LANG = {"python3": "python"}
SECTION_EMOJI = {
    "easy": "👌",
    "medium": "👊",
    "hard": "💪",
}


class SubmissionPage(Page):
    code: str = one("body").regex(
        r"(?:submissionCode\s*:\s*\')(.*)(?:\'\s*,\s*editCodeUrl)",
        lambda match: match.group(1),
    )


@dataclass
class Submission:
    id: str
    statusDisplay: str
    lang: str
    url: str

    @property
    def language(self):
        return LANG_TO_NORMALIZE_LANG.get(self.lang, self.lang)


@dataclass
class Question:
    id: int
    slug: str
    title: str
    difficulty: str
    submissions: Sequence[Submission] = ()
    description: str = None
    solutions: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    metadata: dict = None

    @property
    def name(self):
        return self.title

    @property
    def key(self):
        return self.difficulty

    @property
    def link(self):
        return f"https://leetcode.com/problems/{self.slug}"

    def init_metadata(self):
        self.metadata = {
            "slug": self.slug,
            "submissions": {},
        }

        for submission in self.submissions:
            if submission.language not in self.metadata["submissions"]:
                self.metadata["submissions"][submission.language] = submission.id


@retry
async def submissions_list(client: AsyncClient, slug: str) -> List[Submission]:
    response = await client.request(
        "GET",
        "/graphql",
        json={
            "operationName": "Submissions",
            "variables": {
                "offset": 0,
                "limit": -1,
                "lastKey": None,
                "questionSlug": slug,
            },
            "query": """
                query Submissions($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!) {
                    submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {
                        lastKey
                        hasNext
                        submissions {
                            id
                            statusDisplay
                            lang
                            url
                        }
                        __typename
                    }
                }
                """,
        },
    )
    await response.aread()
    data = response.json()

    return [
        Submission(**submission)
        for submission in data["data"]["submissionList"]["submissions"]
    ]


@retry
async def questions_list(client: AsyncClient) -> List[Question]:
    response = await client.get("/api/problems/all", params={"status": "Solved"})
    await response.aread()
    data = response.json()

    return [
        Question(
            id=questions["stat"]["question_id"],
            slug=questions["stat"]["question__title_slug"],
            title=questions["stat"]["question__title"],
            difficulty=DIFFICULTY_LEVEL[questions["difficulty"]["level"]],
        )
        for questions in data["stat_status_pairs"]
        if questions["status"] == "ac"
    ]


@cached
@retry
async def get_submission_code(client: AsyncClient, submission: Submission) -> str:
    response = await client.get(f"/submissions/detail/{submission.id}/")
    page = SubmissionPage(await response.aread())

    return page.code.encode().decode("unicode-escape")


@retry
async def fetch_solutions(client: AsyncClient, question: Question):
    question.submissions = await submissions_list(client, question.slug)

    language_to_submission = {}
    for submission in question.submissions:
        if submission.language not in language_to_submission:
            language_to_submission[submission.language] = submission

    for lang, submission in language_to_submission.items():
        question.solutions[lang].append(await get_submission_code(client, submission))


@retry
@cached
async def get_description(client: AsyncClient, question: Question) -> str:
    response = await client.request(
        "GET",
        f"/graphql",
        json={
            "operationName": "questionData",
            "variables": {"titleSlug": question.slug},
            "query": """
                    query questionData($titleSlug: String!) {
                        question(titleSlug: $titleSlug) {
                            content
                            __typename
                        }
                    }
                """,
        },
    )
    await response.aread()
    data = response.json()

    return data["data"]["question"]["content"]


@retry
async def fetch_descriptions(client: AsyncClient, question: Question):
    question.description = await get_description(client, question)


def _init_leetcode_cache(book: Book):
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
        lambda client, submission: submissions_map[(submission.id, submission.language)]
    )


async def generate_book(old_book: Optional[Book] = None) -> Book:
    async with AsyncClient(
        base_url="https://leetcode.com",
        cookies={"LEETCODE_SESSION": LEETCODE_SESSION.get()},
    ) as client:
        if old_book is not None:
            _init_leetcode_cache(old_book)

        questions = await questions_list(client)

        for chunk in chunked(questions, CHUNK_SIZE):
            await gather(*(fetch_solutions(client, question) for question in chunk))
            await gather(*(fetch_descriptions(client, question) for question in chunk))

        return Book.from_list(
            questions,
            name="LeetCode 💫",
            section_name=lambda q: f"{SECTION_EMOJI[q.difficulty.lower()]} {q.difficulty.title()}",
            section_sorter_key=DIFFICULTY_LEVEL.index,
            section_reversed=False,
        )


__all__ = ["generate_book"]
