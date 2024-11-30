from fastapi import Request
from fastapi.responses import JSONResponse
from src.utils.exceptions import GeneralAPIError
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger("ExceptionHandler")

async def custom_exception_handler(request: Request, exc: GeneralAPIError):
    logger.error(f"Handling exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

async def validation_exception_handler(request: Request, exc):
    logger.warning(f"Validation error for request {request.url.path}: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "details": exc.errors()},
    )
