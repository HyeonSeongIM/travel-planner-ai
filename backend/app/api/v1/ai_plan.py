from uuid import UUID

from fastapi import APIRouter

from app.schemas.ai_plan import AiPlanRequest, AiPlanResponse

router = APIRouter(prefix="/trips/{trip_id}/ai-plan", tags=["ai-plan"])


@router.post("", response_model=AiPlanResponse, status_code=202)
async def generate_ai_plan(trip_id: UUID, body: AiPlanRequest):
    # AI model integration will be implemented here
    return AiPlanResponse(trip_id=trip_id, message="AI plan generation is not yet implemented.")
