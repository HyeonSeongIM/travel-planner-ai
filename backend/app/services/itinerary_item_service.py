# 여행 일정 항목 비즈니스 로직 레이어
# 일정 항목 조작 전에 반드시 trip 존재 여부를 검증하며, 잘못된 접근은 NotFoundError로 처리한다
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.repository.itinerary_item_repository import ItineraryItemRepository
from app.repository.trip_repository import TripRepository
from app.schemas.itinerary_item import (
    ItineraryItemCreateRequest,
    ItineraryItemResponse,
    ItineraryItemUpdateRequest,
)


class ItineraryItemService:
    def __init__(self, item_repository: ItineraryItemRepository, trip_repository: TripRepository):
        self.item_repository = item_repository
        self.trip_repository = trip_repository

    async def list_items(self, trip_id: UUID) -> list[ItineraryItemResponse]:
        """특정 여행의 일정 항목 목록을 반환한다. trip이 없으면 NotFoundError를 raise한다"""
        if not await self.trip_repository.find_by_id(trip_id):
            raise NotFoundError(f"Trip {trip_id} not found")
        records = await self.item_repository.find_all_by_trip(trip_id)
        return [ItineraryItemResponse.model_validate(r) for r in records]

    async def create_item(self, trip_id: UUID, data: ItineraryItemCreateRequest) -> ItineraryItemResponse:
        """일정 항목을 생성한다. 부모 trip이 없으면 NotFoundError를 raise한다"""
        if not await self.trip_repository.find_by_id(trip_id):
            raise NotFoundError(f"Trip {trip_id} not found")
        record = await self.item_repository.create(trip_id, data)
        return ItineraryItemResponse.model_validate(record)

    async def update_item(
        self, trip_id: UUID, item_id: UUID, data: ItineraryItemUpdateRequest
    ) -> ItineraryItemResponse:
        """일정 항목을 수정한다. 항목이 없거나 해당 trip 소속이 아니면 NotFoundError를 raise한다"""
        item = await self.item_repository.find_by_id(item_id)
        # item이 존재하지 않거나, 다른 trip 소속인 경우 모두 NotFound로 처리 (정보 노출 방지)
        if not item or item["trip_id"] != trip_id:
            raise NotFoundError(f"Itinerary item {item_id} not found")
        record = await self.item_repository.update(item_id, data)
        return ItineraryItemResponse.model_validate(record)

    async def delete_item(self, trip_id: UUID, item_id: UUID) -> None:
        """일정 항목을 삭제한다. 항목이 없거나 해당 trip 소속이 아니면 NotFoundError를 raise한다"""
        item = await self.item_repository.find_by_id(item_id)
        # item이 존재하지 않거나, 다른 trip 소속인 경우 모두 NotFound로 처리 (정보 노출 방지)
        if not item or item["trip_id"] != trip_id:
            raise NotFoundError(f"Itinerary item {item_id} not found")
        await self.item_repository.delete(item_id)
