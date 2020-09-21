from asyncio import gather
from collections import defaultdict
from itertools import count
from json import loads
from typing import List, AsyncIterable, Dict, Optional

from bs4 import Tag
from httpx import AsyncClient, Request

from .context import CODEWARS_USERNAME, CODEWARS_EMAIL, CODEWARS_PASSWORD
from ..models import Book
from ..scrapper import Page, one, many
from ..utils import cached

SECTION_EMOJI = {
    "beta": "🌝",
    "retired": "😶",
    "1 kyu": "🏆",
    "2 kyu": "👑",
    "3 kyu": "💎",
    "4 kyu": "💍",
    "5 kyu": "🎯",
    "6 kyu": "🎩",
    "7 kyu": "🎁",
    "8 kyu": "🎒",
}


class LoginPage(Page):
    auth_token: str = one('input[name="authenticity_token"]').attr("value")


class HomePage(Page):
    username_link: str = one("#header_profile_link").attr("href")


class KataDescriptionPage(Page):
    description: str = one("body").regex(
        r"(?<=data: JSON\.parse\().*(?=\))",
        post_process=lambda match: loads(loads(match.group()))["description"],
    )


class KataPage(Page):
    kuy: str = one(".is-extra-wide span,.tag span").text
    name: str = one("div + a[href]").text
    href: str = one("div + a[href]").attr("href")

    solutions: Dict[str, List[str]]
    description: str
    metadata: dict = {}

    @property
    def key(self):
        return self.kuy

    @property
    def link(self):
        return f"https://www.codewars.com{self.href}"

    def init_metadata(self):
        self.metadata = {"description": self.href}

    def post_init(self, context: Tag):
        # TODO: should be better way to parse it
        self.solutions = defaultdict(list)
        language = None

        for part in context.select(".item-title ~ .markdown, .item-title ~ h6"):
            if part.name == "h6":
                language, *_ = part.text.split(":")
                language = language.strip().lower()
            else:
                assert language is not None, "Language must be set"
                code = part.select_one("code").text
                self.solutions[language].append(code)


class KatasPage(Page):
    katas: List[KataPage] = many(".list-item")


async def katas_stream(client: AsyncClient, chunks: int = 50) -> AsyncIterable:
    async def fetch(page_number: int = 0) -> KatasPage:
        response = await client.get(
            f"/users/{CODEWARS_USERNAME.get()}/completed_solutions",
            params={"page": page_number},
        )
        return KatasPage(await response.aread())

    counter = count()
    provided_katas = set()

    while True:
        for page in await gather(*(fetch(next(counter)) for _ in range(chunks))):
            if not page.katas:
                return

            for solution in page.katas:
                if solution.href not in provided_katas:
                    provided_katas.add(solution.href)
                    yield solution


@cached
async def get_kata_description(client: AsyncClient, kata: KataPage):
    response = await client.get(kata.href)
    kata_desc = KataDescriptionPage(await response.aread())

    return kata_desc.description


async def kata_description(client: AsyncClient, kata: KataPage):
    kata.description = await get_kata_description(client, kata)


async def sign_in(client: AsyncClient):
    response = await client.get("/users/sign_in")
    page = LoginPage(await response.aread())

    response = await client.post(
        f"/users/sign_in",
        data={
            "utf-8": "",
            "authenticity_token": page.auth_token,
            "user[email]": CODEWARS_EMAIL.get(),
            "user[password]": CODEWARS_PASSWORD.get(),
            "user[remember_me]": "true",
        },
    )

    if b"<title>Home | Codewars</title>" not in await response.aread():
        raise RuntimeError("Can't sign up")

    home_page = HomePage(response.content)
    *_, username = home_page.username_link.split("/")

    CODEWARS_USERNAME.set(username)

    def _auth(request: Request) -> Request:
        request.headers.update(
            {"Authorization": page.auth_token, "X-Requested-With": "XMLHttpRequest"}
        )
        return request

    client.auth = _auth


def _init_codewars_cache(book: Book):
    tasks = [task for section in book.sections for task in section.tasks]

    descriptions_map = {
        task.metadata["description"]: task.description for task in tasks
    }

    get_kata_description.add_provider(lambda client, kata: descriptions_map[kata.href])


async def generate_book(old_book: Optional[Book] = None) -> Book:
    async with AsyncClient(base_url="https://www.codewars.com", timeout=30) as client:
        if old_book is not None:
            _init_codewars_cache(old_book)

        await sign_in(client)

        katas = [kata async for kata in katas_stream(client)]
        await gather(*(kata_description(client, kata) for kata in katas))

        return Book.from_list(
            katas,
            name="CodeWars ✨",
            section_name=lambda kata: f"{SECTION_EMOJI[kata.kuy.lower()]} {kata.kuy.title()}",
        )


__all__ = ["generate_book"]
