import re
from pathlib import Path
from typing import List

from . import context, md
from .config import CONFIG, LANG_TO_EMOJI, LANG_TO_PRETTY_LANG
from .names import valid_name, reset_names
from ..models import Book, Section, Task

MD_IF_REGEX = re.compile(
    r"(?:[`~]{3}\s*)(if(?:-not)?):(.*?)\n(.*?)(?:[`~]{3})", re.MULTILINE | re.DOTALL
)
STYLE_REGEX = re.compile(r"<style(?:.*?)>(.*?)</style>", re.MULTILINE | re.DOTALL)


def extract_css_styles(content: str) -> str:
    styles = STYLE_REGEX.findall(content)

    if styles:
        content = STYLE_REGEX.sub("", content)

        for style in styles:
            add_styles(style)

    return content


def add_styles(style: str):
    style_path = context.WEBSITE_CSS.get()

    old_styles = style_path.read_text(encoding="utf-8")
    style_path.write_text(f"{old_styles}\n{style}", encoding="utf-8")


def solve_if_logic(task: Task):
    if MD_IF_REGEX.search(task.description):
        supported_lags = {*task.solutions}

        def replacer(match: re.Match) -> str:
            if_type, langs, if_content = match.groups()
            if_langs = {*langs.strip().split(",")}

            if (if_type == "if") == bool(supported_lags & if_langs):
                return if_content

            return ""

        return MD_IF_REGEX.sub(replacer, task.description)

    return task.description


def generate_task(parent: Path, task: Task):
    def _generate_task():
        yield md.header(md.link(task.name, task.link))
        yield
        yield extract_css_styles(solve_if_logic(task))
        yield
        yield md.header("Solutions")

        for lang, (solution, *_) in task.solutions.items():
            pretty_lang = LANG_TO_PRETTY_LANG.get(lang.lower(), lang.title())

            yield md.header(f"{LANG_TO_EMOJI[lang.lower()]} {pretty_lang}", important=4)
            yield md.code(solution.code, lang)

        yield

    md.readme(parent, _generate_task(), f"{valid_name(task.name, unique=True)}.md")


def generate_section(parent: Path, section: Section):
    root = parent / valid_name(section.name, lower=True)
    root.mkdir(parents=True, exist_ok=True)

    for task in section.tasks:
        generate_task(root, task)


def generate_book(book: Book):
    root = context.DOCS.get() / valid_name(book.name, lower=True)

    for section in book.sections:
        generate_section(root, section)


def generate_summary(books: List[Book]):
    def section_summary(parent: str, section: Section):
        yield md.option(
            md.link(
                name=section.name,
                url=f"/{parent}/{valid_name(section.name, lower=True)}",
                wrap=True,
            )
        )

        for task in section.tasks:
            yield md.option(
                md.link(
                    name=task.name,
                    url=f"/{parent}/{valid_name(section.name, lower=True)}/{valid_name(task.name, unique=True)}.md",
                    wrap=True,
                ),
                ident=4,
            )

    def book_summary(book: Book):
        yield
        yield md.header(book.name)

        for section in book.sections:
            yield from section_summary(valid_name(book.name, lower=True), section)

    def summary():
        yield md.header(CONFIG["title"], important=1)

        for book in books:
            yield from book_summary(book)

    md.readme(context.DOCS.get(), summary(), "SUMMARY.md")
    reset_names()


def generate_docs(books: List[Book], docs_path: Path):
    context.init_context(docs_path)
    generate_summary(books)

    for book in sorted(books, key=lambda b: b.name):
        generate_book(book)


__all__ = ["generate_docs"]
