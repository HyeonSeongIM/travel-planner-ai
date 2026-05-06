# 앱 전역 환경변수를 관리하는 Settings 클래스 — .env 파일을 읽어 설정값을 제공
# 애플리케이션 코드에서는 os.getenv() 대신 반드시 이 모듈의 settings 인스턴스를 사용할 것
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Travel Planner AI"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # .env 파일에서 환경변수를 자동으로 로드
    model_config = {"env_file": ".env"}


# 싱글턴 인스턴스 — 앱 전체에서 이 객체를 import해 사용
settings = Settings()
