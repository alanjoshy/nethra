"""
Shared type definitions and base classes.
"""

from typing import Protocol, TypeVar, Generic
from uuid import UUID

T = TypeVar("T")

__all__ = [
    "Protocol",
    "TypeVar",
    "Generic",
    "UUID",
    "T",
]
