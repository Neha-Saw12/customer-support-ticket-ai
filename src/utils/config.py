import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATA_PATH: str = os.getenv("DATA_PATH", "support_tickets.csv")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.2")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")

settings = Settings()
