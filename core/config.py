from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "GeoAnomaly Pro"
    app_version: str = "1.9.0"
    earth_engine_project: str = "project-f00674bb-1e61-4eec-b16"
    cors_origins: str = "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8080,http://localhost:8080"
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://127.0.0.1:8000/auth/earth-engine/callback"
    frontend_after_ee_callback: str = "http://127.0.0.1:5500/"
    allow_local_ee_auth: bool = True
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
