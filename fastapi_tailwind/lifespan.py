from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

from contextlib import asynccontextmanager

__all__ = (
    "lifespan",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    ...