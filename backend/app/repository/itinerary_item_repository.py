# 여행 일정 항목(ItineraryItem) 저장소 — 인메모리 딕셔너리로 CRUD를 구현
# 이 레이어는 데이터 접근만 담당하며, trip 존재 여부 검증은 Service 레이어가 처리한다
from uuid import UUID, uuid4

from app.schemas.itinerary_item import ItineraryItemCreateRequest, ItineraryItemUpdateRequest

# 프로세스 수명 동안 데이터를 유지하는 인메모리 저장소 (key: item UUID, value: item dict)
_store: dict[UUID, dict] = {}


class ItineraryItemRepository:
    async def find_all_by_trip(self, trip_id: UUID) -> list[dict]:
        """특정 여행에 속한 모든 일정 항목을 day → order 순으로 정렬해 반환한다"""
        items = [item for item in _store.values() if item["trip_id"] == trip_id]
        return sorted(items, key=lambda x: (x["day"], x["order"]))

    async def find_by_id(self, item_id: UUID) -> dict | None:
        """ID로 단일 일정 항목을 조회한다. 없으면 None 반환"""
        return _store.get(item_id)

    async def create(self, trip_id: UUID, data: ItineraryItemCreateRequest) -> dict:
        """새 일정 항목 레코드를 생성하고 저장한다"""
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
        """전달된 필드만 부분 업데이트한다. 대상이 없으면 None 반환"""
        record = _store.get(item_id)
        if not record:
            return None
        # None인 필드는 제외하고 존재하는 필드만 덮어쓴다 (partial update)
        for field, value in data.model_dump(exclude_none=True).items():
            record[field] = value
        return record

    async def delete(self, item_id: UUID) -> bool:
        """일정 항목 레코드를 삭제한다. 삭제 성공 여부를 bool로 반환"""
        if item_id not in _store:
            return False
        del _store[item_id]
        return True
