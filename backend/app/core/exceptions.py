from http import HTTPStatus


class AppError(Exception):
    def __init__(self, message: str, status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, HTTPStatus.NOT_FOUND)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, HTTPStatus.CONFLICT)


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, HTTPStatus.BAD_REQUEST)
