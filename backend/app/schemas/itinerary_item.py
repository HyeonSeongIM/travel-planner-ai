from datetime import time
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ItemCategory(str, Enum):
    ACCOMMODATION = "accommodation"
    TRANSPORT = "transport"
    ACTIVITY = "activity"
    MEAL = "meal"
    OTHER = "other"


class ItineraryItemCreateRequest(BaseModel):
    day: int
    order: int
    title: str
    description: str | None = None
    location: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    category: ItemCategory = ItemCategory.OTHER


class ItineraryItemUpdateRequest(BaseModel):
    day: int | None = None
    order: int | None = None
    title: str | None = None
    description: str | None = None
    location: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    category: ItemCategory | None = None


class ItineraryItemResponse(BaseModel):
    id: UUID
    trip_id: UUID
    day: int
    order: int
    title: str
    description: str | None
    location: str | None
    start_time: time | None
    end_time: time | None
    category: ItemCategory

    model_config = {"from_attributes": True}
