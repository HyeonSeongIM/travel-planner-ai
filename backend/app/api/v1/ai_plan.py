# AI 플랜 생성 엔드포인트 — 현재 stub 상태이며 추후 AI 모델 연동 시 구현 예정
from uuid import UUID

from fastapi import APIRouter

from app.schemas.ai_plan import AiPlanRequest, AiPlanResponse

router = APIRouter(prefix="/trips/{trip_id}/ai-plan", tags=["ai-plan"])


@router.post("", response_model=AiPlanResponse, status_code=202)
async def generate_ai_plan(trip_id: UUID, body: AiPlanRequest):
    """AI 기반 여행 플랜 자동 생성 (stub — 202 Accepted로 수신만 확인)"""
    # AI model integration will be implemented here
    return AiPlanResponse(trip_id=trip_id, message="AI plan generation is not yet implemented.")
