from typing import AsyncGenerator
from app.core.websocket.manager import ConnectionManager
from app.core.websocket.handler import WebSocketHandler

# 创建全局的连接管理器实例
connection_manager = ConnectionManager()
websocket_handler = WebSocketHandler(connection_manager)

def get_connection_manager() -> ConnectionManager:
    """依赖注入：获取WebSocket连接管理器"""
    return connection_manager

def get_websocket_handler() -> WebSocketHandler:
    """依赖注入：获取WebSocket处理器"""
    return websocket_handler

async def shutdown_handler() -> AsyncGenerator:
    """应用关闭时的清理工作"""
    try:
        yield
    finally:
        await websocket_handler.close_all_connections()