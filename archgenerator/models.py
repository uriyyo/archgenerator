from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import dataclass, field
else:
    from pydantic.dataclasses import dataclass


@dataclass
class Solution:
    language: str
    code: str


@dataclass
class Task:
    name: str
    link: str
    description: str | None = None
    solutions: dict[str, list[Solution]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Section:
    name: str
    tasks: list[Task] = field(default_factory=list)


@dataclass
class Book:
    name: str
    sections: list[Section] = field(default_factory=list)


__all__ = [
    "Book",
    "Section",
    "Task",
    "Solution",
]
