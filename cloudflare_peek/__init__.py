"""
CloudflarePeek - A Python utility for scraping Cloudflare-protected websites.

This package provides automatic detection of Cloudflare-protected sites and falls back
to screenshot + OCR extraction when traditional scraping methods fail.
"""

from .core.scraper import peek
from .core.detector import behind_cloudflare

__version__ = "0.1.0"
__author__ = "Talha Ali"
__email__ = "talhaali5365@gmail.com"

__all__ = [
    "peek",
    "behind_cloudflare"
]