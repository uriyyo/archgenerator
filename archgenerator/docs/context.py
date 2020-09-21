import shutil
from contextvars import ContextVar
from pathlib import Path
from typing import Optional

GIT_USERNAME: ContextVar[Optional[str]] = ContextVar("GIT_USERNAME")
GIT_EMAIL: ContextVar[Optional[str]] = ContextVar("GIT_EMAIL")

ROOT: ContextVar[Path] = ContextVar("ROOT")
DOCS: ContextVar[Path] = ContextVar("DOCS")
STYLES_ROOT: ContextVar[Path] = ContextVar("STYLES_ROOT")
WEBSITE_CSS: ContextVar[Path] = ContextVar("WEBSITE_CSS")


def init_context(root: Path):
    ROOT.set(root)
    DOCS.set(root / "docs")
    STYLES_ROOT.set(root / "docs" / "styles")
    WEBSITE_CSS.set(root / "docs" / "styles" / "website.css")

    for p in [*DOCS.get().iterdir(), STYLES_ROOT.get()]:
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)

    STYLES_ROOT.get().mkdir(parents=True)
    WEBSITE_CSS.get().touch()


__all__ = [
    "init_context",
    "ROOT",
    "DOCS",
    "STYLES_ROOT",
    "WEBSITE_CSS",
    "GIT_EMAIL",
    "GIT_USERNAME",
]
