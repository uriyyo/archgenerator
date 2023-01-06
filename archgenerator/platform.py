from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import (
    Protocol,
    runtime_checkable,
    Any,
    Mapping,
    Callable,
    ClassVar,
    TypedDict,
    TypeVar,
    ParamSpec,
    cast,
)

from pkg_resources import iter_entry_points

from .models import Book, Solution, Section, Task

ClickOptionWrapper = Callable[..., Any]


@runtime_checkable
class TaskLike(Protocol):
    name: str
    link: str
    section: str
    description: str | None
    solutions: dict[str, list[str]]
    metadata: dict[str, Any]

    @abstractmethod
    def init_metadata(self) -> None:
        pass


class PlatformConfig(TypedDict):
    title: str
    sections_emoji: Mapping[str, str]


T = TypeVar("T")
P = ParamSpec("P")


class Platform(ABC):
    name: ClassVar[str]
    config: PlatformConfig
    section_reversed: ClassVar[bool] = False
    options: ClassVar[Mapping[str, tuple[ClickOptionWrapper, ContextVar[Any]]]] = {}

    @abstractmethod
    async def fetch(self) -> list[TaskLike]:
        pass

    def init_cache(self, book: Book) -> None:
        pass

    def book_name(self) -> str:
        return self.config["title"]

    def section_name(self, task: TaskLike) -> str:
        return f"{self.config['sections_emoji'][task.section.lower()]} {task.section.title()}"

    def section_sorter_key(self, name: str) -> Any:
        return name

    def wrap_cli(self, cli: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for name, (_, var) in self.options.items():
                var.set(kwargs[name])

            return cli(*args, **kwargs)

        for option, _ in self.options.values():
            wrapper = option(wrapper)

        return cast(Callable[P, T], wrapper)

    async def generate_book(self, old_book: Book | None = None) -> Book:
        if old_book is not None and self.init_cache is not None:
            self.init_cache(old_book)

        tasks = await self.fetch()

        book = Book(name=self.book_name(), sections=[])

        sections = {}
        for t in tasks:
            if t.section not in sections:
                sections[t.section] = Section(name=self.section_name(t), tasks=[])

            t.init_metadata()

            sections[t.section].tasks.append(
                Task(
                    name=t.name,
                    link=t.link,
                    description=t.description,
                    solutions={
                        language: [Solution(language=language, code=solution) for solution in solutions]
                        for language, solutions in t.solutions.items()
                    },
                    metadata=t.metadata,
                )
            )

        for section_name in sorted(sections, reverse=self.section_reversed, key=self.section_sorter_key):
            section = sections[section_name]
            section.tasks.sort(key=lambda t: t.name)
            book.sections.append(section)

        return book


PLATFORMS: dict[str, Platform] = {}


def load_platforms() -> None:
    for entry_point in iter_entry_points("archgenerator"):
        PLATFORMS[entry_point.name] = entry_point.load()()


__all__ = [
    "PLATFORMS",
    "Platform",
    "PlatformConfig",
    "TaskLike",
    "load_platforms",
]
