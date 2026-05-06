# 여행(Trip) 관련 Request/Response Pydantic 스키마 정의
from datetime import date
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, model_validator


class TripStatus(str, Enum):
    """여행의 진행 상태를 나타내는 열거형"""
    PLANNED = "planned"      # 계획됨
    ONGOING = "ongoing"      # 진행 중
    COMPLETED = "completed"  # 완료됨
    CANCELLED = "cancelled"  # 취소됨


class TripCreateRequest(BaseModel):
    """여행 생성 요청 스키마 — 필수/선택 입력값을 정의하고 날짜 유효성을 검증한다"""
    title: str
    destination: str
    start_date: date
    end_date: date
    budget: float | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "TripCreateRequest":
        # 종료일이 시작일보다 이전이면 안 된다
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class TripUpdateRequest(BaseModel):
    """여행 수정 요청 스키마 — 모든 필드가 선택적(partial update)"""
    title: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: TripStatus | None = None
    budget: float | None = None
    notes: str | None = None


class TripResponse(BaseModel):
    """여행 API 응답 스키마 — Repository의 dict 또는 ORM 객체를 직렬화해 반환한다"""
    id: UUID
    title: str
    destination: str
    start_date: date
    end_date: date
    status: TripStatus
    budget: float | None
    notes: str | None

    # ORM 객체(또는 dict)를 그대로 model_validate()에 넘길 수 있도록 허용
    model_config = {"from_attributes": True}
