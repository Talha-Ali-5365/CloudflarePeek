"""Core functionality for CloudflarePeek."""

from .detector import behind_cloudflare
from .scraper import peek

__all__ = ["behind_cloudflare", "peek"]