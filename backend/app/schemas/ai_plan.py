from uuid import UUID

from pydantic import BaseModel


class AiPlanRequest(BaseModel):
    prompt: str | None = None
    style: str | None = None


class AiPlanResponse(BaseModel):
    trip_id: UUID
    message: str

    model_config = {"from_attributes": True}
