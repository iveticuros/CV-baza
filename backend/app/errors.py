from __future__ import annotations

import traceback
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from .config import settings
from .request_context import request_id_ctx


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        rid = request_id_ctx.get() or str(uuid.uuid4())
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"http_{exc.status_code}",
                    "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
                    "request_id": rid,
                }
            },
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        rid = request_id_ctx.get() or str(uuid.uuid4())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Neispravan zahtev.",
                    "request_id": rid,
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError):
        rid = request_id_ctx.get() or str(uuid.uuid4())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Neispravan zahtev.",
                    "request_id": rid,
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_handler(request: Request, exc: SQLAlchemyError):
        rid = request_id_ctx.get() or str(uuid.uuid4())
        body: dict[str, Any] = {
            "error": {
                "code": "database_error",
                "message": "Greška baze podataka.",
                "request_id": rid,
            }
        }
        if settings.ENVIRONMENT != "production":
            body["error"]["debug"] = str(exc)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body)

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        rid = request_id_ctx.get() or str(uuid.uuid4())
        body: dict[str, Any] = {
            "error": {
                "code": "internal_error",
                "message": "Interna greška.",
                "request_id": rid,
            }
        }
        if settings.ENVIRONMENT != "production":
            body["error"]["debug"] = str(exc)
            body["error"]["trace"] = traceback.format_exc()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body)
