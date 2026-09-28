from pydantic_settings import (BaseSettings, SettingsConfigDict)


class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str
    
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    upload_dir: str = "uploads"
    
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
    
settings = Settings()