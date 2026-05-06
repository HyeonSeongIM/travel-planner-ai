from uuid import UUID, uuid4

from app.schemas.trip import TripCreateRequest, TripStatus, TripUpdateRequest

_store: dict[UUID, dict] = {}


class TripRepository:
    async def find_all(self) -> list[dict]:
        return list(_store.values())

    async def find_by_id(self, trip_id: UUID) -> dict | None:
        return _store.get(trip_id)

    async def create(self, data: TripCreateRequest) -> dict:
        trip_id = uuid4()
        record = {
            "id": trip_id,
            "title": data.title,
            "destination": data.destination,
            "start_date": data.start_date,
            "end_date": data.end_date,
            "status": TripStatus.PLANNED,
            "budget": data.budget,
            "notes": data.notes,
        }
        _store[trip_id] = record
        return record

    async def update(self, trip_id: UUID, data: TripUpdateRequest) -> dict | None:
        record = _store.get(trip_id)
        if not record:
            return None
        for field, value in data.model_dump(exclude_none=True).items():
            record[field] = value
        return record

    async def delete(self, trip_id: UUID) -> bool:
        if trip_id not in _store:
            return False
        del _store[trip_id]
        return True
