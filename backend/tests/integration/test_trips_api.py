import pytest
from httpx import AsyncClient

BASE = "/api/v1/trips"

TRIP_PAYLOAD = {
    "title": "도쿄 여행",
    "destination": "일본 도쿄",
    "start_date": "2025-08-01",
    "end_date": "2025-08-05",
    "budget": 1_500_000,
    "notes": "워크샵 겸 관광",
}


async def create_trip(client: AsyncClient, **overrides) -> dict:
    res = await client.post(BASE, json={**TRIP_PAYLOAD, **overrides})
    assert res.status_code == 201
    return res.json()


# --- POST /trips ---

async def test_create_trip_returns_201_with_planned_status(client):
    res = await client.post(BASE, json=TRIP_PAYLOAD)
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "도쿄 여행"
    assert body["status"] == "planned"
    assert "id" in body


async def test_create_trip_end_date_before_start_date_returns_422(client):
    payload = {**TRIP_PAYLOAD, "start_date": "2025-08-10", "end_date": "2025-08-01"}
    res = await client.post(BASE, json=payload)
    assert res.status_code == 422


async def test_create_trip_same_day_is_valid(client):
    """당일치기 여행 (start_date == end_date) 은 유효해야 한다."""
    payload = {**TRIP_PAYLOAD, "start_date": "2025-08-01", "end_date": "2025-08-01"}
    res = await client.post(BASE, json=payload)
    assert res.status_code == 201


async def test_create_trip_optional_fields_can_be_omitted(client):
    payload = {
        "title": "미니멀 여행",
        "destination": "제주도",
        "start_date": "2025-09-01",
        "end_date": "2025-09-03",
    }
    res = await client.post(BASE, json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body["budget"] is None
    assert body["notes"] is None


# --- GET /trips ---

async def test_list_trips_returns_all_created_trips(client):
    await create_trip(client, title="여행 A")
    await create_trip(client, title="여행 B")

    res = await client.get(BASE)
    assert res.status_code == 200
    titles = {t["title"] for t in res.json()}
    assert titles == {"여행 A", "여행 B"}


async def test_list_trips_returns_empty_list_when_none_exist(client):
    res = await client.get(BASE)
    assert res.status_code == 200
    assert res.json() == []


# --- GET /trips/{trip_id} ---

async def test_get_trip_returns_correct_trip(client):
    trip = await create_trip(client)
    res = await client.get(f"{BASE}/{trip['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == trip["id"]


async def test_get_trip_not_found_returns_404(client):
    res = await client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404


# --- PUT /trips/{trip_id} ---

async def test_update_trip_partial_fields_preserves_others(client):
    trip = await create_trip(client)
    res = await client.put(f"{BASE}/{trip['id']}", json={"title": "수정된 제목"})
    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "수정된 제목"
    assert body["destination"] == trip["destination"]   # 나머지 필드는 유지돼야 한다
    assert body["budget"] == trip["budget"]


async def test_update_trip_status_to_ongoing(client):
    trip = await create_trip(client)
    res = await client.put(f"{BASE}/{trip['id']}", json={"status": "ongoing"})
    assert res.status_code == 200
    assert res.json()["status"] == "ongoing"


async def test_update_trip_not_found_returns_404(client):
    res = await client.put(
        f"{BASE}/00000000-0000-0000-0000-000000000000",
        json={"title": "없는 여행"},
    )
    assert res.status_code == 404


# --- DELETE /trips/{trip_id} ---

async def test_delete_trip_returns_204(client):
    trip = await create_trip(client)
    res = await client.delete(f"{BASE}/{trip['id']}")
    assert res.status_code == 204


async def test_delete_trip_removes_trip_from_list(client):
    trip = await create_trip(client)
    await client.delete(f"{BASE}/{trip['id']}")

    res = await client.get(BASE)
    assert all(t["id"] != trip["id"] for t in res.json())


async def test_deleted_trip_returns_404_on_get(client):
    trip = await create_trip(client)
    await client.delete(f"{BASE}/{trip['id']}")

    res = await client.get(f"{BASE}/{trip['id']}")
    assert res.status_code == 404


async def test_delete_trip_not_found_returns_404(client):
    res = await client.delete(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404
