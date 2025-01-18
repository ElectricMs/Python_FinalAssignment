import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings  # 修改这一行

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    # 基础设置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FaceMesh Analysis Server"
    
    # CORS设置
    BACKEND_CORS_ORIGINS: list = ["*"]  # 在生产环境中应该设置具体的域名
    
    # 视频处理设置
    MAX_FPS: int = 30
    FRAME_INTERVAL: float = 1.0 / MAX_FPS
    MAX_FACES: int = 5
    
    # 模型设置
    DETECTION_CONFIDENCE: float = 0.5
    TRACKING_CONFIDENCE: float = 0.5
    
    class Config:
        case_sensitive = True

settings = Settings()