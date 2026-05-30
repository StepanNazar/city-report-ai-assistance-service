from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="AI_ASSISTANCE_")

    database_url: str = "postgresql+asyncpg://ai_user@localhost:5432/ai_assistance"
    database_echo: bool = False

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "ai-assistance-service"
    kafka_enabled: bool = True

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash"

    log_level: str = "INFO"
