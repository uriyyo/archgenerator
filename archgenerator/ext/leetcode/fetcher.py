from collections import defaultdict
from dataclasses import dataclass, field
from typing import Sequence, cast, Any

from httpx import AsyncClient
from selene import browser
from selene.browser import driver
from selene.support.conditions import be
from selene.support.jquery_style_selectors import s

from .config import LANG_TO_NORMALIZE_LANG, DIFFICULTY_LEVEL
from .context import LEETCODE_EMAIL, LEETCODE_PASSWORD, LEETCODE_SESSION
from ...scrapper import Page, one
from ...utils import retry, cached, run_in_executor
from ...web import with_chrome


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
    def language(self) -> str:
        return LANG_TO_NORMALIZE_LANG.get(self.lang, self.lang)


@dataclass
class Question:
    id: int
    slug: str
    title: str
    difficulty: str
    submissions: Sequence[Submission] = ()
    description: str | None = None
    solutions: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.title

    @property
    def section(self) -> str:
        return self.difficulty

    @property
    def link(self) -> str:
        return f"https://leetcode.com/problems/{self.slug}"

    def init_metadata(self) -> None:
        self.metadata = {
            "slug": self.slug,
            "submissions": {},
        }

        for submission in self.submissions:
            if submission.language not in self.metadata["submissions"]:
                self.metadata["submissions"][submission.language] = submission.id


@retry
async def submissions_list(client: AsyncClient, slug: str) -> list[Submission]:
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

    return [Submission(**submission) for submission in data["data"]["submissionList"]["submissions"]]


@retry
async def questions_list(client: AsyncClient) -> list[Question]:
    response = await client.get("/api/problems/all", params={"status": "Solved"})
    await response.aread()
    data = response.json()

    return [
        Question(
            id=questions["stat"]["question_id"],
            slug=questions["stat"]["question__title_slug"],
            title=questions["stat"]["question__title"],
            difficulty=cast(str, DIFFICULTY_LEVEL[questions["difficulty"]["level"]]),
        )
        for questions in data["stat_status_pairs"]
        if questions["status"] == "ac"
    ]


@cached
@retry
async def get_submission_code(client: AsyncClient, submission: Submission) -> str:
    response = await client.post(
        "/graphql",
        json={
            "query": """
                query submissionDetails($submissionId: Int!) {
                    submissionDetails(submissionId: $submissionId) {
                        code
                }
            }
            """,
            "variables": {"submissionId": submission.id},
        },
    )

    await response.aread()
    data = response.json()

    return cast(str, data["data"]["submissionDetails"]["code"])


@retry
async def fetch_solutions(client: AsyncClient, question: Question) -> None:
    question.submissions = await submissions_list(client, question.slug)

    language_to_submission = {}
    for submission in question.submissions:
        if submission.language not in language_to_submission:
            language_to_submission[submission.language] = submission

    for lang, submission in language_to_submission.items():
        question.solutions[lang].append(await get_submission_code(client, submission))


@cached
@retry
async def get_description(client: AsyncClient, question: Question) -> str:
    response = await client.request(
        "GET",
        "/graphql",
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

    return cast(str, data["data"]["question"]["content"])


@retry
async def fetch_descriptions(client: AsyncClient, question: Question) -> None:
    question.description = await get_description(client, question)


@run_in_executor
@with_chrome
def browser_sign_in() -> str:
    browser.open_url("https://leetcode.com/accounts/login/")

    s('[name="login"]').set(LEETCODE_EMAIL.get())
    s('[name="password"]').set(LEETCODE_PASSWORD.get())

    s("#initial-loading").should_not(be.visible)
    s("#signin_btn").should(be.visible).click()

    s(".storyboard").should(be.visible)

    leetcode_session = driver().get_cookie("LEETCODE_SESSION")

    if leetcode_session is None:
        raise RuntimeError("Failed to sign in")

    return cast(str, leetcode_session["value"])


async def sign_in() -> str:
    if leetcode_session := LEETCODE_SESSION.get():
        async with AsyncClient(
            base_url="https://leetcode.com",
            cookies={"LEETCODE_SESSION": leetcode_session},
            follow_redirects=True,
        ) as client:
            response = await client.get("api/problems/all", params={"status": "Solved"})

        if not response.is_error:
            return leetcode_session

    return await browser_sign_in()


__all__ = [
    "questions_list",
    "fetch_solutions",
    "fetch_descriptions",
    "get_description",
    "get_submission_code",
    "sign_in",
]
