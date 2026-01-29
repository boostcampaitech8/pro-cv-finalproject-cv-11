from typing import Any

from fastapi.responses import JSONResponse


def api_response(status_code: int, success: bool, message: str, data: Any = None) -> JSONResponse:
    """Return a consistent API envelope."""
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_code,
            "success": success,
            "message": message,
            "data": data,
        },
    )
