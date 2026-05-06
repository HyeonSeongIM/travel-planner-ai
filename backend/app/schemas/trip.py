from datetime import date
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, model_validator


class TripStatus(str, Enum):
    PLANNED = "planned"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TripCreateRequest(BaseModel):
    title: str
    destination: str
    start_date: date
    end_date: date
    budget: float | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "TripCreateRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class TripUpdateRequest(BaseModel):
    title: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: TripStatus | None = None
    budget: float | None = None
    notes: str | None = None


class TripResponse(BaseModel):
    id: UUID
    title: str
    destination: str
    start_date: date
    end_date: date
    status: TripStatus
    budget: float | None
    notes: str | None

    model_config = {"from_attributes": True}
