from pathlib import Path
from typing import Iterable
from urllib.parse import quote


def link(name: str, url: str, wrap: bool = False) -> str:
    return f"[{name}]({quote(url) if wrap else url})"


def header(content: str, important: int = 2) -> str:
    return f'{"#" * important} {content}'


def option(name: str, ident: int = 0) -> str:
    return " " * ident + f"* {name}"


def code(content: str, lang: str) -> str:
    return f"```{lang}\n{content}\n```"


def readme(root: Path, content: Iterable[str], name: str = "README.md"):
    root.mkdir(parents=True, exist_ok=True)

    readme_path = root / name
    readme_path.write_text("\n".join(s or "" for s in content), encoding="utf-8")


__all__ = ["code", "link", "header", "option", "readme"]
