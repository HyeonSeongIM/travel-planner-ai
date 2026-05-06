# 여행 일정 항목(ItineraryItem) 관련 Request/Response Pydantic 스키마 정의
from datetime import time
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ItemCategory(str, Enum):
    """일정 항목의 카테고리 분류"""
    ACCOMMODATION = "accommodation"  # 숙박
    TRANSPORT = "transport"          # 교통
    ACTIVITY = "activity"            # 액티비티
    MEAL = "meal"                    # 식사
    OTHER = "other"                  # 기타


class ItineraryItemCreateRequest(BaseModel):
    """일정 항목 생성 요청 스키마"""
    day: int             # 여행 몇 일차인지 (1-based)
    order: int           # 같은 날 내 순서 (1-based)
    title: str
    description: str | None = None
    location: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    category: ItemCategory = ItemCategory.OTHER


class ItineraryItemUpdateRequest(BaseModel):
    """일정 항목 수정 요청 스키마 — 모든 필드가 선택적(partial update)"""
    day: int | None = None
    order: int | None = None
    title: str | None = None
    description: str | None = None
    location: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    category: ItemCategory | None = None


class ItineraryItemResponse(BaseModel):
    """일정 항목 API 응답 스키마 — trip_id를 포함해 어느 여행의 항목인지 명시한다"""
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

    # ORM 객체(또는 dict)를 그대로 model_validate()에 넘길 수 있도록 허용
    model_config = {"from_attributes": True}
