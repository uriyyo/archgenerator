import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Match

from bs4 import Tag

from .declarative import Page


@dataclass
class DeclarativeElement(ABC):
    def __set_name__(self, owner: Page, name: str) -> None:
        owner.add_element(name, self)

    @abstractmethod
    def resolve(self, context: Tag, target: Any) -> Any:
        pass


@dataclass
class ElementAttribute(DeclarativeElement):
    parent: DeclarativeElement
    attribute: str

    def resolve(self, context: Tag, target: Any) -> Any:
        context = self.parent.resolve(context, target)
        return context.attrs[self.attribute]


@dataclass
class ElementText(DeclarativeElement):
    parent: DeclarativeElement

    def resolve(self, context: Tag, target: Any) -> Any:
        return self.parent.resolve(context, target).text


@dataclass
class ElementTextRegex(DeclarativeElement):
    parent: DeclarativeElement
    pattern: str
    post_process: Callable[[Any], str] | None = None

    def resolve(self, context: Tag, target: Any) -> Any:
        content = str(self.parent.resolve(context, target))
        match = re.search(self.pattern, content)

        if match is None:
            raise ValueError(f"Regex {self.pattern!r} not found")

        if self.post_process:
            return self.post_process(match)

        return match.group()


@dataclass
class Element(DeclarativeElement, ABC):
    selector: str


@dataclass
class OneElement(Element):
    def regex(self, pattern: str, post_process: Callable[[Match[str]], str] | None = None) -> ElementTextRegex:
        return ElementTextRegex(self, pattern, post_process)

    @property
    def text(self) -> ElementText:
        return ElementText(self)

    def attr(self, attribute: str) -> ElementAttribute:
        return ElementAttribute(self, attribute)

    def resolve(self, context: Tag, target: Any) -> Any:
        return context.select_one(self.selector)


@dataclass
class ManyElements(Element):
    def resolve(self, context: Tag, target: Any) -> Any:
        elements = context.select(self.selector)

        try:
            target_type, *_ = target.__args__
        except AttributeError:
            target_type = target

        if target_type is Any:
            return elements

        return [target_type(e) for e in elements]


def one(selector: str) -> Any:
    return OneElement(selector)


def many(selector: str) -> Any:
    return ManyElements(selector)


__all__ = [
    "DeclarativeElement",
    "one",
    "many",
]
