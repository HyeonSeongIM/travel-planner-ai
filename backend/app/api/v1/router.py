# /api/v1 하위의 모든 도메인 라우터를 한 곳에 집약하는 상위 라우터
# 새 도메인 라우터 추가 시 이 파일에 include_router만 추가하면 된다
from fastapi import APIRouter

from app.api.v1 import ai_plan, itinerary_items, trips

router = APIRouter(prefix="/api/v1")

router.include_router(trips.router)
router.include_router(itinerary_items.router)
router.include_router(ai_plan.router)
