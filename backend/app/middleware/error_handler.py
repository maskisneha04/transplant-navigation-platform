import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": {"code": "HTTP_ERROR", "message": exc.detail}},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Pydantic v2 embeds the raw exception object (e.g. a ValueError from a
        # @field_validator) inside each error's "ctx" — jsonable_encoder converts
        # anything non-serializable (like that exception) to a safe string
        # representation instead of crashing the response with a 500.
        safe_errors = jsonable_encoder(exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": "Invalid request data.", "details": safe_errors},
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Never leak stack traces to the client; log full detail server-side only.
        logger.exception("Unhandled error on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
        )
