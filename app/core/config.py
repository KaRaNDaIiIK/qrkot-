from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки конфигурации приложения и базы данных."""
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    description: str = 'Сбор пожертвований на целевые проекты помощи котам'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )


settings = Settings()
