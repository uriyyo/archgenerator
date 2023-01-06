from asyncio import run
from functools import wraps
from pathlib import Path
from typing import Optional

import click

from ..configurator import load_config
from ..docs import context
from ..docs.commit import commit_docs
from ..docs.generator import generate_docs
from ..models import Book
from ..platform import PLATFORMS, load_platforms, Platform
from ..serializer import load, dump
from ..workflow import init_workflow

DEFAULT_PATH = click.Path(dir_okay=False, writable=True, resolve_path=True)
DEFAULT_DIR_PATH = click.Path(file_okay=False, resolve_path=True)


@click.group()
def main_cli():
    pass


def _init_config(func):
    @click.option("-c", "--config", type=DEFAULT_PATH, default="config.json")
    @wraps(func)
    def wrapper(config: str, **kwargs):
        config_path = Path(config)

        if config_path.exists():
            load_config(config_path)

        return func(config=config, **kwargs)

    return wrapper


def _add_entry_point(platform: Platform):
    @main_cli.command(name=platform.name)
    @click.option("-p", "--path", type=DEFAULT_PATH, default=f"{platform.name}.json")
    @_init_config
    @platform.wrap_cli
    def _entry_point(path: str, **_):
        book_path: Path = Path(path)
        old_book = load(Book, book_path) if book_path.exists() else None

        new_book = run(platform.generate_book(old_book))
        dump(new_book, book_path)


load_platforms()

for p in PLATFORMS.values():
    _add_entry_point(p)


@main_cli.command(name="docs")
@click.option("-p", "--path", type=DEFAULT_DIR_PATH, default=".")
@_init_config
def docs_cli(path: str, **_):
    root = Path(path).resolve()
    books = [load(Book, p) for p in root.glob("*.json") if p.name not in {"book.json", "config.json"}]
    books.sort(key=lambda book: book.name)

    generate_docs(books, root)


@main_cli.command(name="commit")
@click.option("-p", "--path", type=DEFAULT_DIR_PATH, default=".")
@click.option("--push", type=bool, is_flag=True, default=False)
@click.option("--git-email", envvar="GIT_EMAIL", type=str)
@click.option("--git-username", envvar="GIT_USERNAME", type=str)
@_init_config
def docs_commit_cli(
    path: str,
    push: bool = False,
    git_username: Optional[str] = None,
    git_email: Optional[str] = None,
    **_,
):
    context.GIT_EMAIL.set(git_email)
    context.GIT_USERNAME.set(git_username)

    commit_docs(Path(path).resolve(), push)


@main_cli.command(name="init-workflow")
@click.option("-p", "--path", type=DEFAULT_DIR_PATH, default=".")
def docs_init_workflow(path: str):
    init_workflow(Path(path))


__all__ = ["main_cli"]
