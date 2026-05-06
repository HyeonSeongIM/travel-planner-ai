# Trip 데이터 저장소 — 현재 인메모리 딕셔너리를 사용하며 추후 DB(ORM)로 교체 예정
# 이 레이어는 데이터 접근만 담당하며, 비즈니스 로직은 Service 레이어가 처리한다
from uuid import UUID, uuid4

from app.schemas.trip import TripCreateRequest, TripStatus, TripUpdateRequest

# 프로세스 수명 동안 데이터를 유지하는 인메모리 저장소 (key: trip UUID, value: trip dict)
_store: dict[UUID, dict] = {}


class TripRepository:
    async def find_all(self) -> list[dict]:
        """저장된 모든 여행 레코드를 반환한다"""
        return list(_store.values())

    async def find_by_id(self, trip_id: UUID) -> dict | None:
        """ID로 단일 여행 레코드를 조회한다. 없으면 None 반환"""
        return _store.get(trip_id)

    async def create(self, data: TripCreateRequest) -> dict:
        """새 여행 레코드를 생성하고 저장한다. 초기 status는 항상 PLANNED"""
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
        """전달된 필드만 부분 업데이트한다. 대상이 없으면 None 반환"""
        record = _store.get(trip_id)
        if not record:
            return None
        # None인 필드는 제외하고 존재하는 필드만 덮어쓴다 (partial update)
        for field, value in data.model_dump(exclude_none=True).items():
            record[field] = value
        return record

    async def delete(self, trip_id: UUID) -> bool:
        """여행 레코드를 삭제한다. 삭제 성공 여부를 bool로 반환"""
        if trip_id not in _store:
            return False
        del _store[trip_id]
        return True
