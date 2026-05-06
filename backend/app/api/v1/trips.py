# Trip HTTP 엔드포인트 — API 레이어는 HTTP 요청 파싱과 Service 호출만 담당한다
# 비즈니스 로직은 TripService에 위임하며, 상태코드와 response_model은 여기서만 지정한다
from uuid import UUID

from fastapi import APIRouter, Depends

from app.repository.trip_repository import TripRepository
from app.schemas.trip import TripCreateRequest, TripResponse, TripUpdateRequest
from app.services.trip_service import TripService

router = APIRouter(prefix="/trips", tags=["trips"])


# 요청마다 새 TripService 인스턴스를 생성하는 의존성 함수 (추후 DI 컨테이너로 교체 가능)
def get_trip_service() -> TripService:
    return TripService(TripRepository())


@router.get("", response_model=list[TripResponse])
async def list_trips(service: TripService = Depends(get_trip_service)):
    """모든 여행 목록 조회"""
    return await service.list_trips()


@router.post("", response_model=TripResponse, status_code=201)
async def create_trip(body: TripCreateRequest, service: TripService = Depends(get_trip_service)):
    """새 여행 생성"""
    return await service.create_trip(body)


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: UUID, service: TripService = Depends(get_trip_service)):
    """특정 여행 단건 조회"""
    return await service.get_trip(trip_id)


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: UUID, body: TripUpdateRequest, service: TripService = Depends(get_trip_service)
):
    """특정 여행 수정"""
    return await service.update_trip(trip_id, body)


@router.delete("/{trip_id}", status_code=204)
async def delete_trip(trip_id: UUID, service: TripService = Depends(get_trip_service)):
    """특정 여행 삭제 (응답 본문 없음)"""
    await service.delete_trip(trip_id)
