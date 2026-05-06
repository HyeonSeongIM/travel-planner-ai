# FastAPI 앱의 진입점 — 앱 인스턴스 생성, 라우터 등록, 전역 예외 핸들러 등록을 담당
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.router import router
from app.core.config import settings
from app.core.exceptions import AppError

# settings에서 앱 이름과 디버그 모드를 읽어 FastAPI 인스턴스 생성
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


# Service 레이어에서 raise된 AppError 계열 예외를 HTTP 응답으로 변환하는 전역 핸들러
@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


# /api/v1 하위 모든 라우터를 앱에 등록
app.include_router(router)


# 서버 상태 확인용 헬스체크 엔드포인트
@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
