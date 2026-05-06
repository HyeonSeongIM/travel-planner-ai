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
        if not await self.trip_repository.find_by_id(trip_id):
            raise NotFoundError(f"Trip {trip_id} not found")
        records = await self.item_repository.find_all_by_trip(trip_id)
        return [ItineraryItemResponse.model_validate(r) for r in records]

    async def create_item(self, trip_id: UUID, data: ItineraryItemCreateRequest) -> ItineraryItemResponse:
        if not await self.trip_repository.find_by_id(trip_id):
            raise NotFoundError(f"Trip {trip_id} not found")
        record = await self.item_repository.create(trip_id, data)
        return ItineraryItemResponse.model_validate(record)

    async def update_item(
        self, trip_id: UUID, item_id: UUID, data: ItineraryItemUpdateRequest
    ) -> ItineraryItemResponse:
        item = await self.item_repository.find_by_id(item_id)
        if not item or item["trip_id"] != trip_id:
            raise NotFoundError(f"Itinerary item {item_id} not found")
        record = await self.item_repository.update(item_id, data)
        return ItineraryItemResponse.model_validate(record)

    async def delete_item(self, trip_id: UUID, item_id: UUID) -> None:
        item = await self.item_repository.find_by_id(item_id)
        if not item or item["trip_id"] != trip_id:
            raise NotFoundError(f"Itinerary item {item_id} not found")
        await self.item_repository.delete(item_id)
