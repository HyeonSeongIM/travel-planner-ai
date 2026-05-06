# 앱 전용 커스텀 예외 계층 — Service 레이어는 HTTPException 대신 이 예외들만 raise해야 한다
# main.py의 전역 핸들러가 AppError를 캐치해 적절한 HTTP 응답으로 변환한다
from http import HTTPStatus


class AppError(Exception):
    """모든 커스텀 예외의 베이스 클래스. HTTP 상태코드와 메시지를 함께 보유한다."""
    def __init__(self, message: str, status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """리소스를 찾을 수 없을 때 (HTTP 404)"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, HTTPStatus.NOT_FOUND)


class ConflictError(AppError):
    """리소스가 이미 존재해 충돌이 발생했을 때 (HTTP 409)"""
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, HTTPStatus.CONFLICT)


class BadRequestError(AppError):
    """클라이언트 요청이 잘못되었을 때 (HTTP 400)"""
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, HTTPStatus.BAD_REQUEST)
