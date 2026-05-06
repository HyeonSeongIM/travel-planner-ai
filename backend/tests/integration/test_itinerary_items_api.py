import pytest
from httpx import AsyncClient

TRIP_BASE = "/api/v1/trips"

TRIP_PAYLOAD = {
    "title": "도쿄 여행",
    "destination": "일본 도쿄",
    "start_date": "2025-08-01",
    "end_date": "2025-08-05",
}

ITEM_PAYLOAD = {
    "day": 1,
    "order": 1,
    "title": "나리타 공항 도착",
    "location": "나리타 국제공항",
    "category": "transport",
}


async def create_trip(client: AsyncClient) -> dict:
    res = await client.post(TRIP_BASE, json=TRIP_PAYLOAD)
    assert res.status_code == 201
    return res.json()


async def create_item(client: AsyncClient, trip_id: str, **overrides) -> dict:
    url = f"{TRIP_BASE}/{trip_id}/itinerary-items"
    res = await client.post(url, json={**ITEM_PAYLOAD, **overrides})
    assert res.status_code == 201
    return res.json()


def items_url(trip_id: str) -> str:
    return f"{TRIP_BASE}/{trip_id}/itinerary-items"


# --- POST /trips/{trip_id}/itinerary-items ---

async def test_create_item_returns_201_with_trip_id(client):
    trip = await create_trip(client)
    res = await client.post(items_url(trip["id"]), json=ITEM_PAYLOAD)
    assert res.status_code == 201
    body = res.json()
    assert body["trip_id"] == trip["id"]
    assert body["title"] == "나리타 공항 도착"
    assert body["category"] == "transport"
    assert "id" in body


async def test_create_item_trip_not_found_returns_404(client):
    res = await client.post(
        items_url("00000000-0000-0000-0000-000000000000"),
        json=ITEM_PAYLOAD,
    )
    assert res.status_code == 404


async def test_create_item_category_defaults_to_other(client):
    trip = await create_trip(client)
    payload = {k: v for k, v in ITEM_PAYLOAD.items() if k != "category"}
    res = await client.post(items_url(trip["id"]), json=payload)
    assert res.status_code == 201
    assert res.json()["category"] == "other"


# --- GET /trips/{trip_id}/itinerary-items ---

async def test_list_items_sorted_by_day_then_order(client):
    """항목을 무작위 순서로 추가해도 day → order 로 정렬돼 반환돼야 한다."""
    trip = await create_trip(client)
    await create_item(client, trip["id"], day=2, order=1, title="둘째 날 첫 번째")
    await create_item(client, trip["id"], day=1, order=2, title="첫째 날 두 번째")
    await create_item(client, trip["id"], day=1, order=1, title="첫째 날 첫 번째")

    res = await client.get(items_url(trip["id"]))
    assert res.status_code == 200
    titles = [item["title"] for item in res.json()]
    assert titles == ["첫째 날 첫 번째", "첫째 날 두 번째", "둘째 날 첫 번째"]


async def test_list_items_trip_not_found_returns_404(client):
    res = await client.get(items_url("00000000-0000-0000-0000-000000000000"))
    assert res.status_code == 404


async def test_list_items_returns_only_items_of_requested_trip(client):
    """두 여행이 있을 때 각 여행의 항목이 서로 섞이지 않아야 한다."""
    trip_a = await create_trip(client)
    trip_b = await create_trip(client)
    await create_item(client, trip_a["id"], title="A 항목")
    await create_item(client, trip_b["id"], title="B 항목")

    res = await client.get(items_url(trip_a["id"]))
    assert res.status_code == 200
    assert all(item["trip_id"] == trip_a["id"] for item in res.json())
    assert len(res.json()) == 1


# --- PUT /trips/{trip_id}/itinerary-items/{item_id} ---

async def test_update_item_partial_preserves_other_fields(client):
    trip = await create_trip(client)
    item = await create_item(client, trip["id"])

    res = await client.put(
        f"{items_url(trip['id'])}/{item['id']}",
        json={"title": "수정된 항목", "category": "activity"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "수정된 항목"
    assert body["category"] == "activity"
    assert body["location"] == item["location"]   # 수정하지 않은 필드는 유지돼야 한다


async def test_update_item_not_found_returns_404(client):
    trip = await create_trip(client)
    res = await client.put(
        f"{items_url(trip['id'])}/00000000-0000-0000-0000-000000000000",
        json={"title": "없는 항목"},
    )
    assert res.status_code == 404


async def test_update_item_from_different_trip_returns_404(client):
    """다른 여행의 item_id로 수정을 시도하면 404를 반환해야 한다."""
    trip_a = await create_trip(client)
    trip_b = await create_trip(client)
    item = await create_item(client, trip_a["id"])

    res = await client.put(
        f"{items_url(trip_b['id'])}/{item['id']}",
        json={"title": "크로스 트립 수정"},
    )
    assert res.status_code == 404


# --- DELETE /trips/{trip_id}/itinerary-items/{item_id} ---

async def test_delete_item_returns_204(client):
    trip = await create_trip(client)
    item = await create_item(client, trip["id"])

    res = await client.delete(f"{items_url(trip['id'])}/{item['id']}")
    assert res.status_code == 204


async def test_delete_item_removes_from_list(client):
    trip = await create_trip(client)
    item = await create_item(client, trip["id"])
    await client.delete(f"{items_url(trip['id'])}/{item['id']}")

    res = await client.get(items_url(trip["id"]))
    assert all(i["id"] != item["id"] for i in res.json())


async def test_delete_item_from_different_trip_returns_404(client):
    """다른 여행의 item_id로 삭제를 시도하면 404를 반환해야 한다."""
    trip_a = await create_trip(client)
    trip_b = await create_trip(client)
    item = await create_item(client, trip_a["id"])

    res = await client.delete(f"{items_url(trip_b['id'])}/{item['id']}")
    assert res.status_code == 404


async def test_delete_item_not_found_returns_404(client):
    trip = await create_trip(client)
    res = await client.delete(
        f"{items_url(trip['id'])}/00000000-0000-0000-0000-000000000000"
    )
    assert res.status_code == 404
