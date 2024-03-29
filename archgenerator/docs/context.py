import shutil
from contextvars import ContextVar
from pathlib import Path

from .config import CONFIG
from ..serializer import dump

GIT_USERNAME: ContextVar[str | None] = ContextVar("GIT_USERNAME")
GIT_EMAIL: ContextVar[str | None] = ContextVar("GIT_EMAIL")

DOCS: ContextVar[Path] = ContextVar("DOCS")
STYLES_ROOT: ContextVar[Path] = ContextVar("STYLES_ROOT")
WEBSITE_CSS: ContextVar[Path] = ContextVar("WEBSITE_CSS")


def init_context(root: Path) -> None:
    DOCS.set(root)
    STYLES_ROOT.set(root / "styles")
    WEBSITE_CSS.set(root / "styles" / "website.css")

    for p in [*DOCS.get().iterdir(), STYLES_ROOT.get()]:
        if not p.name.startswith(".") and p.is_dir():
            shutil.rmtree(p, ignore_errors=True)

    STYLES_ROOT.get().mkdir(parents=True)
    WEBSITE_CSS.get().touch()

    (root / "README.md").touch(exist_ok=True)

    dump(
        obj={
            "title": CONFIG["title"],
            "root": ".",
            "structure": {"readme": "./README.md", "summary": "./SUMMARY.md"},
            "styles": {"website": "./styles/website.css"},
        },
        path=root / "book.json",
    )


__all__ = [
    "init_context",
    "DOCS",
    "STYLES_ROOT",
    "WEBSITE_CSS",
    "GIT_EMAIL",
    "GIT_USERNAME",
]
