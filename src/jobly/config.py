from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class DatabaseSettings(BaseSettings):
    url: str = "postgresql+asyncpg://postgres:password@localhost:5432/jobly"

    model_config = SettingsConfigDict(env_prefix="DATABASE_")


class RedisSettings(BaseSettings):
    url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class TelegramSettings(BaseSettings):
    bot_token: str = ""
    webhook_url: str = ""
    webhook_secret: str = ""

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")


class MoonshotSettings(BaseSettings):
    api_key: str = ""
    base_url: str = "https://api.moonshot.cn/v1"
    model: str = "kimi-2.6"

    model_config = SettingsConfigDict(env_prefix="MOONSHOT_")


class XenditSettings(BaseSettings):
    secret_key: str = ""
    webhook_token: str = ""

    model_config = SettingsConfigDict(env_prefix="XENDIT_")


class ApifySettings(BaseSettings):
    api_token: str = ""

    model_config = SettingsConfigDict(env_prefix="APIFY_")


class SupabaseSettings(BaseSettings):
    url: str = ""
    key: str = ""
    service_key: str = ""

    model_config = SettingsConfigDict(env_prefix="SUPABASE_")


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    sentry_dsn: str = ""
    admin_telegram_ids: str = ""

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    moonshot: MoonshotSettings = Field(default_factory=MoonshotSettings)
    xendit: XenditSettings = Field(default_factory=XenditSettings)
    apify: ApifySettings = Field(default_factory=ApifySettings)
    supabase: SupabaseSettings = Field(default_factory=SupabaseSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def admin_ids(self) -> list[int]:
        if not self.admin_telegram_ids:
            return []
        return [int(x.strip()) for x in self.admin_telegram_ids.split(",") if x.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
