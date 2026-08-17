"""Helpers for constructing GrewMatch requests from the UI fields."""

from grewpy import Request


class EmptyPatternError(ValueError):
    """Raised when no main GrewMatch pattern was provided."""


def build_request(pattern: str, without: str | None = None) -> Request:
    """Build a Grew request from bare ``pattern`` and ``without`` bodies."""
    pattern = pattern.strip()
    if not pattern:
        raise EmptyPatternError("Enter a GrewMatch pattern before submitting the query.")

    request = Request().pattern(pattern)

    if without and (without := without.strip()):
        request = request.without(without)

    return request
