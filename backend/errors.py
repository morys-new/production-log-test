from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(
        self, code: str, message: str, status_code: int = 400
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Wrap FastAPI's request validation errors in the same envelope as ApiError."""
    first = exc.errors()[0]
    # loc starts with where the value came from: "body", "query" or "path".
    field = ".".join(str(part) for part in first["loc"][1:])
    message = f"{field}: {first['msg']}" if field else str(first["msg"])
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": message}},
    )
