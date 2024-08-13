from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Awaitable, Any, Coroutine

    from fastapi import Request
    from starlette.responses import Response

from starlette.middleware.base import BaseHTTPMiddleware

__all__ = (
    "TailwindCSSMiddleware",
)

class TailwindCSSMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Coroutine[Any, Any, Response]:

        response = await call_next(request)
        return response