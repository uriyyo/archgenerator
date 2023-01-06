from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar, get_type_hints

from bs4 import BeautifulSoup, Tag

if TYPE_CHECKING:
    from .elements import DeclarativeElement

T = TypeVar("T")


@dataclass
class _PageElement:
    type: type
    element: DeclarativeElement


class Page:
    __elements__: dict[str, _PageElement]

    def __init__(self, source: str | bytes | Tag) -> None:
        context = source if isinstance(source, Tag) else BeautifulSoup(source, features="html.parser")

        for name, page_element in self.__elements__.items():
            setattr(self, name, page_element.element.resolve(context, page_element.type))

        self.post_init(context)

    def __repr__(self) -> str:
        attrs = {attr: getattr(self, attr) for attr in self.__elements__}
        attrs_repr = ", ".join(f"{k}={v!r}" for k, v in attrs.items())

        return f"{type(self).__name__}({attrs_repr})"

    def post_init(self, context: Tag) -> None:
        pass

    @classmethod
    def add_element(cls, name: str, element: DeclarativeElement) -> None:
        if "__elements__" not in cls.__dict__:
            cls.__elements__ = {}

        cls.__elements__[name] = _PageElement(
            type=get_type_hints(cls).get(name, str),
            element=element,
        )


__all__ = [
    "Page",
]
