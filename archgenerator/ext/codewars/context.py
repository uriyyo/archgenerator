from contextvars import ContextVar

CODEWARS_EMAIL: ContextVar[str] = ContextVar("CODEWARS_EMAIL")
CODEWARS_PASSWORD: ContextVar[str] = ContextVar("CODEWARS_PASSWORD")
CODEWARS_USERNAME: ContextVar[str] = ContextVar("CODEWARS_USERNAME")

__all__ = [
    "CODEWARS_EMAIL",
    "CODEWARS_PASSWORD",
    "CODEWARS_USERNAME",
]
