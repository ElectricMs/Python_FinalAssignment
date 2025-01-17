import cv2
import asyncio
from typing import Optional
from app.core.websocket.manager import ConnectionManager
from app.schemas.metrics import ProcessingResponse
from app.utils.image import encode_image_to_base64
from app.config import settings


# 调试日志
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WebSocketHandler:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.active_captures = {}

    async def handle_connection(self, client_id: str):
        """处理新的WebSocket连接"""
        try:
            # 初始化摄像头
            cap = await self._initialize_capture(client_id)
            if not cap:
                return

            # 开始处理视频流
            await self._process_video_stream(client_id, cap)

        except Exception as e:
            await self._handle_error(client_id, str(e))
        
        finally:
            await self._cleanup(client_id)

    async def _initialize_capture(self, client_id: str) -> Optional[cv2.VideoCapture]:
        """初始化视频捕获"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            await self.manager.send_message(
                client_id,
                ProcessingResponse(
                    status="error",
                    error="Cannot access webcam"
                )
            )
            return None

        self.active_captures[client_id] = cap
        return cap

    async def _process_video_stream(self, client_id: str, cap: cv2.VideoCapture):
        """处理视频流"""
        processor = self.manager.get_processor(client_id)
        
        while True:
            # 检查连接是否仍然活跃
            if client_id not in self.manager.active_connections:
                break

            # 读取视频帧
            ret, frame = cap.read()
            if not ret:
                await self._handle_error(client_id, "Failed to capture frame")
                break

            try:
                # 处理帧
                processed_frame, metrics_list = processor.process_frame(frame)
                
                # 调试日志
                logger.debug(f"Raw metrics type: {type(metrics_list)}")
                logger.debug(f"Raw metrics content: {metrics_list}")
                
                # 确保 metrics 是列表
                if not isinstance(metrics_list, list):
                    metrics_list = [metrics_list]
                
                # 转换 metrics 为字典列表
                metrics_dict_list = []
                for metric in metrics_list:
                    if hasattr(metric, 'dict'):
                        metric_dict = metric.dict()
                    elif hasattr(metric, 'model_dump'):
                        metric_dict = metric.model_dump()
                    else:
                        metric_dict = dict(metric)
                    metrics_dict_list.append(metric_dict)
                
                # 创建响应
                response = ProcessingResponse(
                    status="success",
                    image=encode_image_to_base64(processed_frame),
                    metrics=metrics_dict_list
                )
                
                # 调试日志
                logger.debug(f"Final response type: {type(response)}")
                logger.debug(f"Final response content: {response.model_dump()}")
                
                # 发送响应
                await self.manager.send_message(client_id, response)
                
                # 控制帧率
                await asyncio.sleep(settings.FRAME_INTERVAL)
                
            except Exception as e:
                await self._handle_error(client_id, f"Frame processing error: {str(e)}")

    async def _handle_error(self, client_id: str, error_message: str):
        """处理错误情况"""
        try:
            await self.manager.send_message(
                client_id,
                ProcessingResponse(
                    status="error",
                    error=error_message
                )
            )
        except Exception:
            pass

    async def _cleanup(self, client_id: str):
        """清理资源"""
        # 释放摄像头
        if client_id in self.active_captures:
            self.active_captures[client_id].release()
            del self.active_captures[client_id]

        # 断开连接
        await self.manager.disconnect(client_id)

    async def close_all_connections(self):
        """关闭所有连接和资源"""
        # 获取所有客户端ID的副本
        client_ids = list(self.active_captures.keys())
        
        # 关闭每个连接
        for client_id in client_ids:
            await self._cleanup(client_id)
        
        # 确保所有连接都被清理
        await self.manager.clear_all_connections()