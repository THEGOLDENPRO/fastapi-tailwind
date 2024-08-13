from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.staticfiles import StaticFiles

__all__ = (
    "compile"
)

def compile(destination_source: StaticFiles) -> None:
    ...