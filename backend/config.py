"""
配置文件
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # App
    APP_NAME: str = "报告生成工具"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    # Database
    DB_TYPE: str = "mysql"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "report_generator"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "sqlite":
            return "sqlite:///./sql_app.db"
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Coze API
    COZE_API_KEY: str = ""
    COZE_BASE_URL: str = "https://api.coze.cn"
    COZE_WORKFLOW_ID: str = ""
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    OUTPUT_DIR: str = "./outputs"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
