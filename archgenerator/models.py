from typing import List, Optional, Dict

from pydantic.dataclasses import dataclass


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


__all__ = ["Book", "Section", "Task", "Solution"]
