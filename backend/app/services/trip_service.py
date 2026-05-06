from uuid import UUID

from app.core.exceptions import NotFoundError
from app.repository.trip_repository import TripRepository
from app.schemas.trip import TripCreateRequest, TripResponse, TripUpdateRequest


class TripService:
    def __init__(self, repository: TripRepository):
        self.repository = repository

    async def list_trips(self) -> list[TripResponse]:
        records = await self.repository.find_all()
        return [TripResponse.model_validate(r) for r in records]

    async def get_trip(self, trip_id: UUID) -> TripResponse:
        record = await self.repository.find_by_id(trip_id)
        if not record:
            raise NotFoundError(f"Trip {trip_id} not found")
        return TripResponse.model_validate(record)

    async def create_trip(self, data: TripCreateRequest) -> TripResponse:
        record = await self.repository.create(data)
        return TripResponse.model_validate(record)

    async def update_trip(self, trip_id: UUID, data: TripUpdateRequest) -> TripResponse:
        record = await self.repository.update(trip_id, data)
        if not record:
            raise NotFoundError(f"Trip {trip_id} not found")
        return TripResponse.model_validate(record)

    async def delete_trip(self, trip_id: UUID) -> None:
        deleted = await self.repository.delete(trip_id)
        if not deleted:
            raise NotFoundError(f"Trip {trip_id} not found")
