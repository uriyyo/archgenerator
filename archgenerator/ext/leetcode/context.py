from contextvars import ContextVar

LEETCODE_SESSION: ContextVar[str] = ContextVar("LEETCODE_SESSION")

__all__ = ["LEETCODE_SESSION"]
