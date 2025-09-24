"""
JOBA 프로젝트 공통 예외 클래스
"""

class JOBAException(Exception):
    """JOBA 프로젝트 기본 예외 클래스"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

class ValidationError(JOBAException):
    """유효성 검증 오류 (400)"""
    def __init__(self, message: str):
        super().__init__(message, 400)

class NotFoundError(JOBAException):
    """리소스를 찾을 수 없음 (404)"""
    def __init__(self, message: str):
        super().__init__(message, 404)

class UnauthorizedError(JOBAException):
    """인증 필요 (401)"""
    def __init__(self, message: str):
        super().__init__(message, 401)

class ForbiddenError(JOBAException):
    """권한 없음 (403)"""
    def __init__(self, message: str):
        super().__init__(message, 403)

class ConflictError(JOBAException):
    """충돌 오류 (409)"""
    def __init__(self, message: str):
        super().__init__(message, 409)

class InternalServerError(JOBAException):
    """내부 서버 오류 (500)"""
    def __init__(self, message: str):
        super().__init__(message, 500)
