import asyncio
from typing import Union
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, timeout: Union[int, float]):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), self.timeout)
        except asyncio.TimeoutError:
            return JSONResponse(
                {"detail": f"Request took longer than {self.timeout}s and was cancelled"},
                status_code=504,
            )