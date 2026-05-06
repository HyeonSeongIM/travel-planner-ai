from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.router import router
from app.core.config import settings
from app.core.exceptions import AppError

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
