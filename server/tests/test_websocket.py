import pytest
import pytest_asyncio
import asyncio
import numpy as np
from unittest.mock import patch, MagicMock, AsyncMock
from app.core.websocket.handler import WebSocketHandler
from app.schemas.metrics import ProcessingResponse

# ====== 测试夹具 ======
@pytest_asyncio.fixture
async def websocket_handler(connection_manager):
    """创建WebSocket处理器实例"""
    handler = WebSocketHandler(connection_manager)
    yield handler
    # 测试后清理
    await handler.close_all_connections()
    
@pytest.fixture
def mock_websocket():
    """创建模拟的WebSocket连接"""
    socket = AsyncMock()
    socket.send_json = AsyncMock()
    socket.receive_json = AsyncMock()
    socket.close = AsyncMock()
    return socket

@pytest.fixture
def mock_video_capture():
    """创建模拟的视频捕获对象"""
    capture = MagicMock()
    # 模拟读取帧
    capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
    capture.isOpened.return_value = True
    return capture

# ====== 测试用例 ======
@pytest.mark.asyncio
async def test_websocket_connection(websocket_handler, mock_websocket):
    """测试WebSocket连接处理"""
    client_id = "test_client"
    
    # 模拟连接
    await websocket_handler.manager.connect(mock_websocket, client_id)
    
    # 验证连接是否建立
    assert client_id in websocket_handler.manager.active_connections
    assert client_id in websocket_handler.manager.processors

    # 清理
    websocket_handler.manager.disconnect(client_id)

@pytest.mark.asyncio
async def test_video_processing(websocket_handler, mock_websocket, mock_video_capture):
    """测试视频处理流程"""
    client_id = "test_client"
    
    # 模拟连接
    await websocket_handler.manager.connect(mock_websocket, client_id)
    
    with patch('cv2.VideoCapture', return_value=mock_video_capture):
        # 启动处理
        processing_task = asyncio.create_task(
            websocket_handler.handle_connection(client_id)
        )
        
        # 等待一小段时间以允许处理几帧
        await asyncio.sleep(0.1)
        
        # 手动断开连接
        websocket_handler.manager.disconnect(client_id)
        
        # 等待处理任务完成
        await processing_task

@pytest.mark.asyncio
async def test_error_handling(websocket_handler, mock_websocket):
    """测试错误处理"""
    client_id = "test_client"
    
    # 模拟连接
    await websocket_handler.manager.connect(mock_websocket, client_id)
    
    # 模拟发送错误消息
    error_message = "Test error"
    await websocket_handler._handle_error(client_id, error_message)
    
    # 验证错误消息是否被正确发送
    mock_websocket.send_json.assert_called_once()
    
    # 清理
    websocket_handler.manager.disconnect(client_id)

@pytest.mark.asyncio
async def test_cleanup(websocket_handler, mock_websocket, mock_video_capture):
    """测试资源清理"""
    client_id = "test_client"
    
    # 模拟连接和摄像头
    await websocket_handler.manager.connect(mock_websocket, client_id)
    websocket_handler.active_captures[client_id] = mock_video_capture
    
    # 执行清理
    await websocket_handler._cleanup(client_id)
    
    # 验证清理结果
    assert client_id not in websocket_handler.active_captures
    assert client_id not in websocket_handler.manager.active_connections
    assert client_id not in websocket_handler.manager.processors
    # 验证视频捕获是否被释放
    mock_video_capture.release.assert_called_once()

@pytest.mark.asyncio
async def test_multiple_connections(websocket_handler):
    """测试多个连接的处理"""
    # 创建多个模拟WebSocket连接
    mock_sockets = [AsyncMock() for _ in range(3)]
    client_ids = [f"client_{i}" for i in range(3)]
    
    # 建立连接
    for socket, client_id in zip(mock_sockets, client_ids):
        await websocket_handler.manager.connect(socket, client_id)
    
    # 验证所有连接都被正确建立
    for client_id in client_ids:
        assert client_id in websocket_handler.manager.active_connections
        assert client_id in websocket_handler.manager.processors
    
    # 关闭所有连接
    await websocket_handler.close_all_connections()
    
    # 验证所有连接都被正确关闭
    assert len(websocket_handler.manager.active_connections) == 0
    assert len(websocket_handler.manager.processors) == 0

if __name__ == '__main__':
    pytest.main([__file__, "-v"])