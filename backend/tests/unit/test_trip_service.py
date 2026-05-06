from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.trip import TripCreateRequest, TripStatus, TripUpdateRequest
from app.services.trip_service import TripService


def make_trip_record(**kwargs) -> dict:
    defaults = {
        "id": uuid4(),
        "title": "도쿄 여행",
        "destination": "일본 도쿄",
        "start_date": date(2025, 8, 1),
        "end_date": date(2025, 8, 5),
        "status": TripStatus.PLANNED,
        "budget": None,
        "notes": None,
    }
    return {**defaults, **kwargs}


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_repo) -> TripService:
    return TripService(mock_repo)


# --- list_trips ---

async def test_list_trips_returns_all(service, mock_repo):
    mock_repo.find_all.return_value = [
        make_trip_record(title="도쿄 여행"),
        make_trip_record(title="파리 여행"),
    ]
    result = await service.list_trips()
    assert len(result) == 2
    assert {r.title for r in result} == {"도쿄 여행", "파리 여행"}


async def test_list_trips_empty(service, mock_repo):
    mock_repo.find_all.return_value = []
    assert await service.list_trips() == []


# --- get_trip ---

async def test_get_trip_returns_correct_response(service, mock_repo):
    trip_id = uuid4()
    mock_repo.find_by_id.return_value = make_trip_record(id=trip_id, title="도쿄 여행")

    result = await service.get_trip(trip_id)

    assert result.id == trip_id
    assert result.title == "도쿄 여행"
    mock_repo.find_by_id.assert_called_once_with(trip_id)


async def test_get_trip_not_found_raises_not_found_error(service, mock_repo):
    mock_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        await service.get_trip(uuid4())


# --- create_trip ---

async def test_create_trip_initial_status_is_planned(service, mock_repo):
    data = TripCreateRequest(
        title="도쿄 여행",
        destination="일본 도쿄",
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 5),
    )
    mock_repo.create.return_value = make_trip_record()

    result = await service.create_trip(data)

    assert result.status == TripStatus.PLANNED
    mock_repo.create.assert_called_once_with(data)


async def test_create_trip_returns_trip_response_with_all_fields(service, mock_repo):
    trip_id = uuid4()
    mock_repo.create.return_value = make_trip_record(id=trip_id, budget=1_500_000, notes="워크샵")
    data = TripCreateRequest(
        title="도쿄 여행",
        destination="일본 도쿄",
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 5),
        budget=1_500_000,
        notes="워크샵",
    )

    result = await service.create_trip(data)

    assert result.id == trip_id
    assert result.budget == 1_500_000
    assert result.notes == "워크샵"


# --- update_trip ---

async def test_update_trip_returns_updated_response(service, mock_repo):
    trip_id = uuid4()
    mock_repo.update.return_value = make_trip_record(id=trip_id, title="수정된 제목")

    result = await service.update_trip(trip_id, TripUpdateRequest(title="수정된 제목"))

    assert result.title == "수정된 제목"
    mock_repo.update.assert_called_once()


async def test_update_trip_not_found_raises_not_found_error(service, mock_repo):
    mock_repo.update.return_value = None
    with pytest.raises(NotFoundError):
        await service.update_trip(uuid4(), TripUpdateRequest(title="없는 여행"))


async def test_update_trip_status_change(service, mock_repo):
    trip_id = uuid4()
    mock_repo.update.return_value = make_trip_record(id=trip_id, status=TripStatus.ONGOING)

    result = await service.update_trip(trip_id, TripUpdateRequest(status=TripStatus.ONGOING))

    assert result.status == TripStatus.ONGOING


# --- delete_trip ---

async def test_delete_trip_calls_repository_delete(service, mock_repo):
    trip_id = uuid4()
    mock_repo.delete.return_value = True

    await service.delete_trip(trip_id)

    mock_repo.delete.assert_called_once_with(trip_id)


async def test_delete_trip_not_found_raises_not_found_error(service, mock_repo):
    mock_repo.delete.return_value = False
    with pytest.raises(NotFoundError):
        await service.delete_trip(uuid4())
