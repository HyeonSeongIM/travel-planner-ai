from uuid import UUID

from fastapi import APIRouter, Depends

from app.repository.itinerary_item_repository import ItineraryItemRepository
from app.repository.trip_repository import TripRepository
from app.schemas.itinerary_item import (
    ItineraryItemCreateRequest,
    ItineraryItemResponse,
    ItineraryItemUpdateRequest,
)
from app.services.itinerary_item_service import ItineraryItemService

router = APIRouter(prefix="/trips/{trip_id}/itinerary-items", tags=["itinerary-items"])


def get_itinerary_service() -> ItineraryItemService:
    return ItineraryItemService(ItineraryItemRepository(), TripRepository())


@router.get("", response_model=list[ItineraryItemResponse])
async def list_items(trip_id: UUID, service: ItineraryItemService = Depends(get_itinerary_service)):
    return await service.list_items(trip_id)


@router.post("", response_model=ItineraryItemResponse, status_code=201)
async def create_item(
    trip_id: UUID,
    body: ItineraryItemCreateRequest,
    service: ItineraryItemService = Depends(get_itinerary_service),
):
    return await service.create_item(trip_id, body)


@router.put("/{item_id}", response_model=ItineraryItemResponse)
async def update_item(
    trip_id: UUID,
    item_id: UUID,
    body: ItineraryItemUpdateRequest,
    service: ItineraryItemService = Depends(get_itinerary_service),
):
    return await service.update_item(trip_id, item_id, body)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    trip_id: UUID,
    item_id: UUID,
    service: ItineraryItemService = Depends(get_itinerary_service),
):
    await service.delete_item(trip_id, item_id)
