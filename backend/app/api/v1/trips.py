from uuid import UUID

from fastapi import APIRouter, Depends

from app.repository.trip_repository import TripRepository
from app.schemas.trip import TripCreateRequest, TripResponse, TripUpdateRequest
from app.services.trip_service import TripService

router = APIRouter(prefix="/trips", tags=["trips"])


def get_trip_service() -> TripService:
    return TripService(TripRepository())


@router.get("", response_model=list[TripResponse])
async def list_trips(service: TripService = Depends(get_trip_service)):
    return await service.list_trips()


@router.post("", response_model=TripResponse, status_code=201)
async def create_trip(body: TripCreateRequest, service: TripService = Depends(get_trip_service)):
    return await service.create_trip(body)


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: UUID, service: TripService = Depends(get_trip_service)):
    return await service.get_trip(trip_id)


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: UUID, body: TripUpdateRequest, service: TripService = Depends(get_trip_service)
):
    return await service.update_trip(trip_id, body)


@router.delete("/{trip_id}", status_code=204)
async def delete_trip(trip_id: UUID, service: TripService = Depends(get_trip_service)):
    await service.delete_trip(trip_id)
