from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_DB_URL: str
    MYSQL_DB_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DB_TYPE: str
    
    # SMTP Configuration
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_USE_TLS: bool
    
    @property
    def DATABASE_URL(self):
        if self.DB_TYPE == "postgres":
            return self.POSTGRES_DB_URL
        elif self.DB_TYPE == "mysql":
            return self.MYSQL_DB_URL
        
        raise ValueError("Unsupported DB_TYPE")
            
    model_config = SettingsConfigDict(env_file='.env', extra="ignore")
            
settings = Settings()