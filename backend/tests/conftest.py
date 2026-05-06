import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

import app.repository.itinerary_item_repository as item_repo_module
import app.repository.trip_repository as trip_repo_module
from app.main import app


@pytest.fixture(autouse=True)
def reset_stores():
    """각 테스트 전후로 인메모리 저장소를 비워 테스트 간 상태 오염을 방지한다."""
    trip_repo_module._store.clear()
    item_repo_module._store.clear()
    yield
    trip_repo_module._store.clear()
    item_repo_module._store.clear()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """실제 앱을 ASGI 레벨에서 호출하는 비동기 HTTP 클라이언트 픽스처."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
