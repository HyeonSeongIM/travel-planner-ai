# AI 플랜 생성 Request/Response Pydantic 스키마 — 현재 stub 상태이며 추후 AI 모델 연동 시 확장 예정
from uuid import UUID

from pydantic import BaseModel


class AiPlanRequest(BaseModel):
    """AI 플랜 생성 요청 스키마 — 사용자가 원하는 여행 스타일이나 프롬프트를 선택적으로 전달한다"""
    prompt: str | None = None  # 사용자 자유 입력 프롬프트 (예: "맛집 위주로 짜줘")
    style: str | None = None   # 여행 스타일 힌트 (예: "relaxed", "packed")


class AiPlanResponse(BaseModel):
    """AI 플랜 생성 응답 스키마"""
    trip_id: UUID   # 플랜이 생성된 여행의 ID
    message: str    # AI 응답 메시지 또는 처리 결과 안내

    model_config = {"from_attributes": True}
