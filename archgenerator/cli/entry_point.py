from asyncio import run
from pathlib import Path
from typing import Callable, Awaitable
from typing import Optional

import click

from ..docs.generator import generate_docs
from ..docs.commit import commit_docs
from ..docs import context as docs_context
from ..fetchers import codewars, leetcode, context as fetcher_context
from ..models import Book

DEFAULT_PATH = click.Path(dir_okay=False, writable=True, resolve_path=True)
DEFAULT_DIR_PATH = click.Path(file_okay=False, resolve_path=True)


@click.group()
def main_cli():
    pass


@main_cli.command(name="leetcode")
@click.option("--session-id", envvar="LEETCODE_SESSION_ID", type=str, required=True)
@click.option("-p", "--path", type=DEFAULT_PATH, default="leetcode.json")
def leetcode_cli(session_id: str, path: str):
    fetcher_context.LEETCODE_SESSION.set(session_id)

    run(_entry_point(leetcode.generate_book, path))


@main_cli.command(name="codewars")
@click.option("--email", envvar="CODEWARS_EMAIL", type=str, required=True)
@click.option("--password", envvar="CODEWARS_PASSWORD", type=str, required=True)
@click.option("-p", "--path", type=DEFAULT_PATH, default="codewars.json")
def codewars_cli(email: str, password: str, path: str):
    fetcher_context.CODEWARS_EMAIL.set(email)
    fetcher_context.CODEWARS_PASSWORD.set(password)

    run(_entry_point(codewars.generate_book, path))


@main_cli.command(name="docs")
@click.option("-p", "--path", type=DEFAULT_DIR_PATH, default=".")
def docs_cli(path: str):
    root = Path(path).resolve()
    books = [Book.from_file(p) for p in root.glob("*.json") if p.name != "book.json"]

    generate_docs(books, root)


@main_cli.command(name="commit")
@click.option("-p", "--path", type=DEFAULT_DIR_PATH, default=".")
@click.option("--push", type=bool, is_flag=True, default=False)
@click.option("--git-email", envvar="GIT_EMAIL", type=str)
@click.option("--git-username", envvar="GIT_USERNAME", type=str)
def docs_cli(
    path: str,
    push: bool = False,
    git_username: Optional[str] = None,
    git_email: Optional[str] = None,
):
    docs_context.GIT_EMAIL.set(git_email)
    docs_context.GIT_USERNAME.set(git_username)

    root = Path(path).resolve()
    commit_docs(root, push)


async def _entry_point(
    generator: Callable[[Optional[Book]], Awaitable[Book]], path: str,
):
    book_path: Path = Path(path)
    old_book = Book.from_file(book_path) if book_path.exists() else None

    book = await generator(old_book)
    book.dump_to_file(book_path)


__all__ = ["main_cli"]
