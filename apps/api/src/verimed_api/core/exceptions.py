"""Domain exceptions and FastAPI exception handlers returning ErrorResponse envelopes."""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from verimed_api.schemas.common import ErrorBody, ErrorDetail, ErrorResponse


class AppError(Exception):
    """Base application domain exception."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: list[ErrorDetail] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers so all errors follow ErrorResponse schema."""

    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        payload = ErrorResponse(
            error=ErrorBody(
                code=exc.code,
                message=exc.message,
                details=exc.details,
            )
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=payload.model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            ErrorDetail(
                field=".".join(str(loc) for loc in err.get("loc", []) if loc != "body") or None,
                issue=err.get("msg", "Invalid value"),
            )
            for err in exc.errors()
        ]
        payload = ErrorResponse(
            error=ErrorBody(
                code="VALIDATION_ERROR",
                message="Request payload validation failed.",
                details=details,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=payload.model_dump(mode="json"),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_request: Request, exc: HTTPException) -> JSONResponse:
        payload = ErrorResponse(
            error=ErrorBody(
                code=f"HTTP_{exc.status_code}",
                message=str(exc.detail),
                details=[],
            )
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=payload.model_dump(mode="json"),
        )
