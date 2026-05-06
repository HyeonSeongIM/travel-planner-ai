# Travel Planner AI

AI 기반 여행 계획 서비스. 여행 일정을 생성·관리하고, AI가 최적의 여행 플랜을 제안합니다.

---

## 목차

- [기술 스택](#기술-스택)
- [아키텍처](#아키텍처)
- [프로젝트 구조](#프로젝트-구조)
- [기능 목록](#기능-목록)
- [실행 방법](#실행-방법)
- [API 엔드포인트](#api-엔드포인트)

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | FastAPI, Uvicorn |
| Frontend | Streamlit *(미구현)* |
| AI | Anthropic Claude, OpenAI |
| Data 검증 | Pydantic v2 |
| HTTP 클라이언트 | httpx |
| 설정 관리 | pydantic-settings |

---

## 아키텍처

**Clean Architecture** 4계층 구조를 채택합니다. 의존성은 항상 바깥 → 안쪽 방향으로만 흐릅니다.

```
HTTP 요청
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  API Layer  (app/api/v1/)                               │
│  - HTTP 요청 수신 및 스키마 파싱                          │
│  - Service 호출 후 HTTP 응답 반환                        │
│  - 비즈니스 로직 금지 / HTTPException 만 사용             │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Service Layer  (app/services/)                         │
│  - 모든 비즈니스 로직의 소유자                            │
│  - Repository 조합 후 Response 스키마 반환               │
│  - AppError 계열 예외만 raise (HTTPException 금지)       │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Repository Layer  (app/repository/)                    │
│  - 데이터 저장소 접근만 담당                              │
│  - 현재 인메모리 딕셔너리 사용 (추후 DB로 교체 예정)       │
│  - dict 반환 (스키마 변환은 Service 담당)                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Schema Layer  (app/schemas/)                           │
│  - Request: 입력값 검증 (model_validator로 교차 필드 검증)│
│  - Response: API 응답 직렬화 (from_attributes=True)      │
└─────────────────────────────────────────────────────────┘
```

### 에러 흐름

```
Service에서 NotFoundError(AppError) raise
    │
    ▼
main.py의 @app.exception_handler(AppError) 캐치
    │
    ▼
JSONResponse(status_code, {"detail": "..."}) 반환
```

커스텀 예외는 `app/core/exceptions.py`의 `AppError`를 상속해 추가합니다.

---

## 프로젝트 구조

```
travel-planner-ai/
├── main.py                          # 루트 진입점 (backend/app/main.py 재노출)
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI 앱 생성, 라우터·예외 핸들러 등록
│   │   ├── core/
│   │   │   ├── config.py            # 환경변수 관리 (Settings / pydantic-settings)
│   │   │   └── exceptions.py        # 커스텀 예외 계층 (AppError, NotFoundError 등)
│   │   ├── schemas/
│   │   │   ├── trip.py              # Trip Request/Response 스키마
│   │   │   ├── itinerary_item.py    # ItineraryItem Request/Response 스키마
│   │   │   └── ai_plan.py           # AI 플랜 Request/Response 스키마
│   │   ├── repository/
│   │   │   ├── trip_repository.py          # Trip 인메모리 CRUD
│   │   │   └── itinerary_item_repository.py# ItineraryItem 인메모리 CRUD
│   │   ├── services/
│   │   │   ├── trip_service.py             # Trip 비즈니스 로직
│   │   │   └── itinerary_item_service.py   # ItineraryItem 비즈니스 로직
│   │   └── api/
│   │       └── v1/
│   │           ├── router.py        # /api/v1 하위 라우터 집약
│   │           ├── trips.py         # Trip HTTP 엔드포인트
│   │           ├── itinerary_items.py # ItineraryItem HTTP 엔드포인트
│   │           └── ai_plan.py       # AI 플랜 HTTP 엔드포인트 (stub)
│   ├── requirements.txt
│   └── .env.example
└── frontend/                        # Streamlit 프론트엔드 (미구현)
```

---

## 기능 목록

### 여행 관리 (Trip)

| 기능 | 설명 |
|------|------|
| 여행 생성 | 제목, 목적지, 기간, 예산, 메모를 입력해 여행을 생성합니다. 종료일이 시작일보다 이전이면 400 에러를 반환합니다. |
| 여행 목록 조회 | 저장된 모든 여행을 반환합니다. |
| 여행 단건 조회 | ID로 특정 여행을 조회합니다. |
| 여행 수정 | 여행의 필드를 부분 수정합니다 (Partial Update). 상태(planned / ongoing / completed / cancelled) 변경 포함. |
| 여행 삭제 | 여행과 연결된 모든 데이터를 삭제합니다. |

### 일정 항목 관리 (Itinerary Item)

| 기능 | 설명 |
|------|------|
| 일정 항목 추가 | 특정 여행에 항목(숙박·교통·액티비티·식사 등)을 추가합니다. day와 order로 순서를 관리합니다. |
| 일정 항목 목록 조회 | 여행의 일정 항목을 day → order 순으로 정렬해 반환합니다. |
| 일정 항목 수정 | 항목의 필드를 부분 수정합니다. |
| 일정 항목 삭제 | 특정 항목을 삭제합니다. |

### AI 플랜 생성 (AI Plan) *(stub)*

| 기능 | 설명 |
|------|------|
| AI 플랜 생성 | 사용자의 프롬프트와 여행 스타일을 바탕으로 AI가 일정을 자동 생성합니다. (현재 미구현) |

---

## 실행 방법

### 1. 저장소 클론 및 의존성 설치

```bash
git clone <repository-url>
cd travel-planner-ai

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r backend/requirements.txt
```

### 2. 환경변수 설정

```bash
cp backend/.env.example backend/.env
# backend/.env 파일을 열어 필요한 값을 수정하세요
```

```dotenv
APP_NAME=Travel Planner AI
DEBUG=false
API_V1_PREFIX=/api/v1
```

### 3. 서버 실행

```bash
cd backend
uvicorn app.main:app --reload
```

서버가 실행되면 아래 주소로 접근할 수 있습니다.

| 주소 | 설명 |
|------|------|
| http://localhost:8000/docs | Swagger UI (API 테스트) |
| http://localhost:8000/redoc | ReDoc (API 문서) |
| http://localhost:8000/health | 헬스체크 |

---

## API 엔드포인트

### Health

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 확인 |

### Trip

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/v1/trips` | 여행 목록 조회 |
| POST | `/api/v1/trips` | 여행 생성 |
| GET | `/api/v1/trips/{trip_id}` | 여행 단건 조회 |
| PUT | `/api/v1/trips/{trip_id}` | 여행 수정 |
| DELETE | `/api/v1/trips/{trip_id}` | 여행 삭제 |

### Itinerary Item

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/v1/trips/{trip_id}/itinerary-items` | 일정 항목 목록 조회 |
| POST | `/api/v1/trips/{trip_id}/itinerary-items` | 일정 항목 추가 |
| PUT | `/api/v1/trips/{trip_id}/itinerary-items/{item_id}` | 일정 항목 수정 |
| DELETE | `/api/v1/trips/{trip_id}/itinerary-items/{item_id}` | 일정 항목 삭제 |

### AI Plan

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/v1/trips/{trip_id}/ai-plan` | AI 플랜 생성 *(stub)* |

### 요청/응답 예시

**여행 생성 (POST /api/v1/trips)**

```json
// Request
{
  "title": "도쿄 여행",
  "destination": "일본 도쿄",
  "start_date": "2025-08-01",
  "end_date": "2025-08-05",
  "budget": 1500000,
  "notes": "팀 회식 겸 워크샵"
}

// Response 201
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "도쿄 여행",
  "destination": "일본 도쿄",
  "start_date": "2025-08-01",
  "end_date": "2025-08-05",
  "status": "planned",
  "budget": 1500000,
  "notes": "팀 회식 겸 워크샵"
}
```

**일정 항목 추가 (POST /api/v1/trips/{trip_id}/itinerary-items)**

```json
// Request
{
  "day": 1,
  "order": 1,
  "title": "나리타 공항 도착",
  "location": "나리타 국제공항",
  "start_time": "10:30:00",
  "category": "transport"
}

// Response 201
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "day": 1,
  "order": 1,
  "title": "나리타 공항 도착",
  "description": null,
  "location": "나리타 국제공항",
  "start_time": "10:30:00",
  "end_time": null,
  "category": "transport"
}
```
