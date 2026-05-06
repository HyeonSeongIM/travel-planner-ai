# FastAPI Project Convention

---

## 프로젝트 구조

```
travel-planner-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱 진입점. 라우터 등록 및 전역 예외 핸들러 등록
│   │   ├── core/
│   │   │   ├── config.py        # 환경변수 관리 (Settings). .env 파일을 읽어 앱 설정을 제공
│   │   │   └── exceptions.py    # 커스텀 예외 정의 (AppError 계열). HTTP 상태코드와 메시지를 함께 보유
│   │   ├── schemas/
│   │   │   ├── trip.py          # 여행 계획 Request/Response 스키마
│   │   │   ├── itinerary_item.py# 일정 항목 Request/Response 스키마
│   │   │   └── ai_plan.py       # AI 플랜 생성 Request/Response 스키마 (stub)
│   │   ├── repository/
│   │   │   ├── trip_repository.py          # Trip CRUD. 현재 인메모리 딕셔너리 사용 (추후 DB로 교체)
│   │   │   └── itinerary_item_repository.py# ItineraryItem CRUD. 인메모리
│   │   ├── services/
│   │   │   ├── trip_service.py             # Trip 비즈니스 로직 (유효성 검사, NotFoundError 등)
│   │   │   └── itinerary_item_service.py   # ItineraryItem 비즈니스 로직. trip 존재 여부도 함께 검증
│   │   └── api/
│   │       └── v1/
│   │           ├── router.py        # /api/v1 하위 라우터를 한 곳에 집약
│   │           ├── trips.py         # Trip HTTP 엔드포인트 (GET/POST/PUT/DELETE /api/v1/trips)
│   │           ├── itinerary_items.py # 일정 항목 엔드포인트 (/api/v1/trips/{id}/itinerary-items)
│   │           └── ai_plan.py       # AI 플랜 엔드포인트 stub (POST /api/v1/trips/{id}/ai-plan)
│   ├── requirements.txt
│   └── .env.example
└── frontend/                        # Streamlit 프론트엔드 (미구현)
```

---

## 레이어 역할 및 데이터 흐름

```
HTTP 요청
   │
   ▼
[API Layer]  app/api/v1/*.py
   - FastAPI 라우터. HTTP 요청을 받아 스키마로 파싱하고 Service를 호출
   - HTTPException, 상태코드, response_model 지정은 여기서만
   - 비즈니스 로직 절대 금지
   │
   ▼
[Service Layer]  app/services/*.py
   - 모든 비즈니스 로직의 소유자
   - Repository를 조합해 로직 수행 후 Response 스키마를 반환
   - 에러는 AppError 계열(NotFoundError 등)만 raise. HTTPException 금지
   │
   ▼
[Repository Layer]  app/repository/*.py
   - DB(현재 인메모리) 접근만 담당
   - dict 또는 ORM 레코드를 반환 (스키마 변환은 Service가 담당)
   - 트랜잭션 경계는 Service가 관리
   │
   ▼
[Schema Layer]  app/schemas/*.py
   - Request: 입력값 검증 및 파싱 (model_validator로 교차 필드 검증)
   - Response: API 응답 직렬화. from_attributes=True로 ORM 객체도 수용
```

**Request → Response 예시 (Trip 생성):**
```
POST /api/v1/trips
  → trips.py (API): TripCreateRequest 파싱 → TripService.create_trip() 호출
  → trip_service.py (Service): 로직 수행 → TripRepository.create() 호출
  → trip_repository.py (Repository): _store에 저장 → dict 반환
  → trip_service.py: TripResponse.model_validate(dict) 반환
  → trips.py: FastAPI가 TripResponse를 JSON 직렬화 → HTTP 201 응답
```

---

## 에러 흐름

```
Service에서 NotFoundError(AppError) raise
   │
   ▼
main.py의 @app.exception_handler(AppError)가 캐치
   │
   ▼
JSONResponse(status_code=404, content={"detail": "..."}) 반환
```

커스텀 예외 추가 시: `app/core/exceptions.py`에 `AppError`를 상속해서 추가

---

## 현재 엔드포인트 목록

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 서버 헬스 체크 |
| GET | `/api/v1/trips` | 여행 목록 조회 |
| POST | `/api/v1/trips` | 여행 생성 |
| GET | `/api/v1/trips/{trip_id}` | 여행 단건 조회 |
| PUT | `/api/v1/trips/{trip_id}` | 여행 수정 |
| DELETE | `/api/v1/trips/{trip_id}` | 여행 삭제 |
| GET | `/api/v1/trips/{trip_id}/itinerary-items` | 일정 항목 목록 조회 |
| POST | `/api/v1/trips/{trip_id}/itinerary-items` | 일정 항목 추가 |
| PUT | `/api/v1/trips/{trip_id}/itinerary-items/{item_id}` | 일정 항목 수정 |
| DELETE | `/api/v1/trips/{trip_id}/itinerary-items/{item_id}` | 일정 항목 삭제 |
| POST | `/api/v1/trips/{trip_id}/ai-plan` | AI 플랜 생성 (stub) |

---

## 서버 실행

```bash
cd backend
uvicorn app.main:app --reload
# Swagger UI: http://localhost:8000/docs
```

---

## Architecture (Clean Architecture)
- **API Layer** (`app/api/`): HTTP handling only. No business logic allowed.
- **Service Layer** (`app/services/`): Owns all business logic. No direct ORM usage. Never raise `HTTPException` here.
- **Repository Layer** (`app/repository/`): DB access only. Transaction boundaries are managed by the Service layer.
- **Schema Layer** (`app/schemas/`): Strictly separate Request/Response models. Use `model_validate` (Pydantic v2).

## Naming
- Files/variables: `snake_case` | Classes: `PascalCase` | Constants: `UPPER_SNAKE_CASE`
- Schemas: `UserCreateRequest`, `UserResponse`
- API routes: plural nouns + kebab-case (`/api/v1/order-items`)
- Celery tasks: verb-first (`send_welcome_email`)

## Async Rules
- All I/O must use `async/await` (use `asyncpg`, `httpx`).
- Never call blocking code (`requests`, `time.sleep`) inside `async def` — use `asyncio.to_thread()` instead.
- Delegate CPU-bound work to Celery workers.

## Error Handling
- Define custom exceptions in `app/core/exceptions.py` (inherit from `AppError`).
- Never raise `HTTPException` in the Service layer. Use custom exceptions only.
- Register a global handler in `main.py` via `@app.exception_handler(AppError)`.

## Config
- Manage all environment variables through `Settings(BaseSettings)` in `app/core/config.py`.
- Never call `os.getenv()` directly in application code.

## DB & Migrations
- Always include an Alembic revision file when changing a model.
- Migration message format: `add_index_to_users_email`

## Testing
- Unit: Test Service logic with mocked repositories. No DB required.
- Integration: Use `httpx.AsyncClient` against a test DB.
- Maintain ≥ 80% coverage on the Service layer.