# Trip 비즈니스 로직 레이어 — Repository를 조합해 로직을 수행하고 Response 스키마를 반환한다
# 에러는 AppError 계열만 raise하며, HTTPException을 직접 사용하지 않는다
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.repository.trip_repository import TripRepository
from app.schemas.trip import TripCreateRequest, TripResponse, TripUpdateRequest


class TripService:
    def __init__(self, repository: TripRepository):
        self.repository = repository

    async def list_trips(self) -> list[TripResponse]:
        """저장된 모든 여행 목록을 반환한다"""
        records = await self.repository.find_all()
        return [TripResponse.model_validate(r) for r in records]

    async def get_trip(self, trip_id: UUID) -> TripResponse:
        """단일 여행을 조회한다. 존재하지 않으면 NotFoundError를 raise한다"""
        record = await self.repository.find_by_id(trip_id)
        if not record:
            raise NotFoundError(f"Trip {trip_id} not found")
        return TripResponse.model_validate(record)

    async def create_trip(self, data: TripCreateRequest) -> TripResponse:
        """새 여행을 생성하고 반환한다"""
        record = await self.repository.create(data)
        return TripResponse.model_validate(record)

    async def update_trip(self, trip_id: UUID, data: TripUpdateRequest) -> TripResponse:
        """여행 정보를 부분 수정한다. 존재하지 않으면 NotFoundError를 raise한다"""
        record = await self.repository.update(trip_id, data)
        if not record:
            raise NotFoundError(f"Trip {trip_id} not found")
        return TripResponse.model_validate(record)

    async def delete_trip(self, trip_id: UUID) -> None:
        """여행을 삭제한다. 존재하지 않으면 NotFoundError를 raise한다"""
        deleted = await self.repository.delete(trip_id)
        if not deleted:
            raise NotFoundError(f"Trip {trip_id} not found")
