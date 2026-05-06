from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.itinerary_item import (
    ItemCategory,
    ItineraryItemCreateRequest,
    ItineraryItemUpdateRequest,
)
from app.services.itinerary_item_service import ItineraryItemService


def make_item_record(trip_id=None, **kwargs) -> dict:
    defaults = {
        "id": uuid4(),
        "trip_id": trip_id or uuid4(),
        "day": 1,
        "order": 1,
        "title": "나리타 공항 도착",
        "description": None,
        "location": "나리타 국제공항",
        "start_time": None,
        "end_time": None,
        "category": ItemCategory.TRANSPORT,
    }
    return {**defaults, **kwargs}


@pytest.fixture
def mock_item_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_trip_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_item_repo, mock_trip_repo) -> ItineraryItemService:
    return ItineraryItemService(mock_item_repo, mock_trip_repo)


# --- list_items ---

async def test_list_items_raises_when_trip_not_found(service, mock_trip_repo):
    mock_trip_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        await service.list_items(uuid4())


async def test_list_items_returns_items_for_trip(service, mock_item_repo, mock_trip_repo):
    trip_id = uuid4()
    mock_trip_repo.find_by_id.return_value = {"id": trip_id}
    mock_item_repo.find_all_by_trip.return_value = [
        make_item_record(trip_id=trip_id, day=1, order=1),
        make_item_record(trip_id=trip_id, day=1, order=2),
    ]

    result = await service.list_items(trip_id)

    assert len(result) == 2
    assert all(r.trip_id == trip_id for r in result)
    mock_item_repo.find_all_by_trip.assert_called_once_with(trip_id)


# --- create_item ---

async def test_create_item_raises_when_trip_not_found(service, mock_trip_repo):
    mock_trip_repo.find_by_id.return_value = None
    data = ItineraryItemCreateRequest(day=1, order=1, title="테스트 항목")
    with pytest.raises(NotFoundError):
        await service.create_item(uuid4(), data)


async def test_create_item_returns_response_with_correct_trip_id(service, mock_item_repo, mock_trip_repo):
    trip_id = uuid4()
    mock_trip_repo.find_by_id.return_value = {"id": trip_id}
    record = make_item_record(trip_id=trip_id, title="나리타 공항 도착")
    mock_item_repo.create.return_value = record

    data = ItineraryItemCreateRequest(day=1, order=1, title="나리타 공항 도착")
    result = await service.create_item(trip_id, data)

    assert result.trip_id == trip_id
    assert result.title == "나리타 공항 도착"
    mock_item_repo.create.assert_called_once_with(trip_id, data)


# --- update_item ---

async def test_update_item_raises_when_item_not_found(service, mock_item_repo):
    mock_item_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        await service.update_item(uuid4(), uuid4(), ItineraryItemUpdateRequest())


async def test_update_item_raises_when_item_belongs_to_different_trip(service, mock_item_repo):
    """item은 존재하지만 요청한 trip_id와 소속이 다르면 NotFoundError를 발생시킨다."""
    other_trip_id = uuid4()
    mock_item_repo.find_by_id.return_value = make_item_record(trip_id=other_trip_id)

    with pytest.raises(NotFoundError):
        await service.update_item(uuid4(), uuid4(), ItineraryItemUpdateRequest(title="크로스 수정"))


async def test_update_item_returns_updated_response(service, mock_item_repo):
    trip_id = uuid4()
    item_id = uuid4()
    mock_item_repo.find_by_id.return_value = make_item_record(id=item_id, trip_id=trip_id)
    mock_item_repo.update.return_value = make_item_record(
        id=item_id, trip_id=trip_id, title="수정된 항목", category=ItemCategory.ACTIVITY
    )

    result = await service.update_item(trip_id, item_id, ItineraryItemUpdateRequest(title="수정된 항목"))

    assert result.title == "수정된 항목"
    assert result.category == ItemCategory.ACTIVITY
    mock_item_repo.update.assert_called_once_with(item_id, ItineraryItemUpdateRequest(title="수정된 항목"))


# --- delete_item ---

async def test_delete_item_raises_when_item_not_found(service, mock_item_repo):
    mock_item_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        await service.delete_item(uuid4(), uuid4())


async def test_delete_item_raises_when_item_belongs_to_different_trip(service, mock_item_repo):
    """item은 존재하지만 요청한 trip_id와 소속이 다르면 NotFoundError를 발생시킨다."""
    other_trip_id = uuid4()
    mock_item_repo.find_by_id.return_value = make_item_record(trip_id=other_trip_id)

    with pytest.raises(NotFoundError):
        await service.delete_item(uuid4(), uuid4())


async def test_delete_item_calls_repository_delete(service, mock_item_repo):
    trip_id = uuid4()
    item_id = uuid4()
    mock_item_repo.find_by_id.return_value = make_item_record(id=item_id, trip_id=trip_id)

    await service.delete_item(trip_id, item_id)

    mock_item_repo.delete.assert_called_once_with(item_id)
