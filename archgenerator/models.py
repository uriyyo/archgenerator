from json import loads, dumps
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable

from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder


@dataclass
class Solution:
    language: str
    code: str


@dataclass
class Task:
    name: str
    link: str
    description: Optional[str] = None
    solutions: Dict[str, List[Solution]] = None
    metadata: Optional[dict] = None


@dataclass
class Section:
    name: str
    tasks: List[Task] = None


@dataclass
class Book:
    name: str
    sections: List[Section] = None

    @classmethod
    def from_list(
        cls,
        tasks: List[Any],
        name: str,
        section_name: Callable[[str], str],
        section_sorter_key: Callable = None,
        section_reversed: bool = True,
    ):
        book = cls(name=name, sections=[])

        sections = {}
        for t in tasks:
            if t.key not in sections:
                sections[t.key] = Section(name=section_name(t), tasks=[])

            t.init_metadata()

            sections[t.key].tasks.append(
                Task(
                    name=t.name,
                    link=t.link,
                    description=t.description,
                    solutions={
                        language: [
                            Solution(language=language, code=solution)
                            for solution in solutions
                        ]
                        for language, solutions in t.solutions.items()
                    },
                    metadata=t.metadata,
                )
            )

        for section_name in sorted(
            sections, reverse=section_reversed, key=section_sorter_key
        ):
            section = sections[section_name]
            section.tasks.sort(key=lambda t: t.name)
            book.sections.append(section)

        return book

    @classmethod
    def from_file(cls, path: Path):
        return cls(**loads(path.read_text(encoding="utf-8")))

    def dump_to_file(self, path: Path):
        path.write_text(dumps(self, indent=4, default=pydantic_encoder))


__all__ = ["Book", "Section", "Task", "Solution"]
