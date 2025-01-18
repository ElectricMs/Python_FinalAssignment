from typing import Dict, Any
from fastapi import WebSocket
from app.core.facemesh.processor import EnhancedFaceMeshProcessor
from app.schemas.metrics import WebSocketMessage, ProcessingResponse

import logging
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.processors: Dict[str, EnhancedFaceMeshProcessor] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """建立新的WebSocket连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.processors[client_id] = EnhancedFaceMeshProcessor()

    async def disconnect(self, client_id: str):
        """断开指定客户端的连接"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].close()
            except Exception:
                pass  # 忽略关闭连接时的错误
            del self.active_connections[client_id]
        
        if client_id in self.processors:
            del self.processors[client_id]

    async def send_message(self, client_id: str, message: ProcessingResponse):
        """发送消息给指定客户端"""
        try:
            # 首先转换为字典
            message_dict = message.model_dump(exclude_none=True)
            
            # 创建 WebSocket 消息
            websocket_message = WebSocketMessage(
                type="frame_processed",
                data=message_dict
            )
            
            # 转换为 JSON 并发送
            final_message = websocket_message.model_dump(exclude_none=True)
            logger.debug(f"Sending message: {final_message}")
            
            await self.active_connections[client_id].send_json(final_message)
            
        except Exception as e:
            logger.exception(f"Error sending message to client {client_id}")
            raise

    def get_processor(self, client_id: str) -> EnhancedFaceMeshProcessor:
        """获取指定客户端的处理器"""
        return self.processors.get(client_id)

    async def broadcast(self, message: Any):
        """广播消息给所有连接的客户端"""
        for connection in self.active_connections.values():
            await connection.send_json(message)

    async def clear_all_connections(self):
        """强制清理所有连接"""
        for client_id in list(self.active_connections.keys()):
            await self.disconnect(client_id)
        self.active_connections.clear()
        self.processors.clear()