# 여행 일정 항목 HTTP 엔드포인트 — /api/v1/trips/{trip_id}/itinerary-items 하위 라우터
# trip_id를 경로 파라미터로 받아 항상 특정 여행 컨텍스트 내에서 항목을 조작한다
from uuid import UUID

from fastapi import APIRouter, Depends

from app.repository.itinerary_item_repository import ItineraryItemRepository
from app.repository.trip_repository import TripRepository
from app.schemas.itinerary_item import (
    ItineraryItemCreateRequest,
    ItineraryItemResponse,
    ItineraryItemUpdateRequest,
)
from app.services.itinerary_item_service import ItineraryItemService

router = APIRouter(prefix="/trips/{trip_id}/itinerary-items", tags=["itinerary-items"])


# 요청마다 새 ItineraryItemService 인스턴스를 생성하는 의존성 함수
def get_itinerary_service() -> ItineraryItemService:
    return ItineraryItemService(ItineraryItemRepository(), TripRepository())


@router.get("", response_model=list[ItineraryItemResponse])
async def list_items(trip_id: UUID, service: ItineraryItemService = Depends(get_itinerary_service)):
    """특정 여행의 일정 항목 목록 조회 (day → order 정렬)"""
    return await service.list_items(trip_id)


@router.post("", response_model=ItineraryItemResponse, status_code=201)
async def create_item(
    trip_id: UUID,
    body: ItineraryItemCreateRequest,
    service: ItineraryItemService = Depends(get_itinerary_service),
):
    """특정 여행에 일정 항목 추가"""
    return await service.create_item(trip_id, body)


@router.put("/{item_id}", response_model=ItineraryItemResponse)
async def update_item(
    trip_id: UUID,
    item_id: UUID,
    body: ItineraryItemUpdateRequest,
    service: ItineraryItemService = Depends(get_itinerary_service),
):
    """특정 일정 항목 수정"""
    return await service.update_item(trip_id, item_id, body)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    trip_id: UUID,
    item_id: UUID,
    service: ItineraryItemService = Depends(get_itinerary_service),
):
    """특정 일정 항목 삭제 (응답 본문 없음)"""
    await service.delete_item(trip_id, item_id)
