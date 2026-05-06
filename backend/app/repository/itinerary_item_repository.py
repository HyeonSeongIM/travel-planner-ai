from uuid import UUID, uuid4

from app.schemas.itinerary_item import ItineraryItemCreateRequest, ItineraryItemUpdateRequest

_store: dict[UUID, dict] = {}


class ItineraryItemRepository:
    async def find_all_by_trip(self, trip_id: UUID) -> list[dict]:
        items = [item for item in _store.values() if item["trip_id"] == trip_id]
        return sorted(items, key=lambda x: (x["day"], x["order"]))

    async def find_by_id(self, item_id: UUID) -> dict | None:
        return _store.get(item_id)

    async def create(self, trip_id: UUID, data: ItineraryItemCreateRequest) -> dict:
        item_id = uuid4()
        record = {
            "id": item_id,
            "trip_id": trip_id,
            "day": data.day,
            "order": data.order,
            "title": data.title,
            "description": data.description,
            "location": data.location,
            "start_time": data.start_time,
            "end_time": data.end_time,
            "category": data.category,
        }
        _store[item_id] = record
        return record

    async def update(self, item_id: UUID, data: ItineraryItemUpdateRequest) -> dict | None:
        record = _store.get(item_id)
        if not record:
            return None
        for field, value in data.model_dump(exclude_none=True).items():
            record[field] = value
        return record

    async def delete(self, item_id: UUID) -> bool:
        if item_id not in _store:
            return False
        del _store[item_id]
        return True
