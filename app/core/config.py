import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 불러오기

class Settings:
    POSTGRES_URL: str = os.getenv("POSTGRES_URL")
    UPSTAGE_API_KEY: str = os.getenv("UPSTAGE_API_KEY")
    APP_SECRET: str = os.getenv("APP_SECRET", "dev-secret")  # fallback 값

settings = Settings()
