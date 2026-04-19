from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_DB_URL: str
    MYSQL_DB_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DB_TYPE: str
    
    @property
    def DATABASE_URL(self):
        match self.DB_TYPE:
            case "postgres":
                return self.POSTGRES_DB_URL
            case "mysql":
                return self.MYSQL_DB_URL
            case _:
                raise ValueError("Unsupported DB_TYPE")
            
    model_config = SettingsConfigDict(env_file='.env', extra="ignore")
            
settings = Settings()