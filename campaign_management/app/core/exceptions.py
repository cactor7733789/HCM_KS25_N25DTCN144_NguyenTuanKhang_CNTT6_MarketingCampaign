from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "message": exc.detail
        }
    )
