import pytest
import pytest_asyncio
import numpy as np
import cv2
from fastapi.testclient import TestClient
from app.main import app
from app.core.facemesh.processor import EnhancedFaceMeshProcessor
from app.core.websocket.manager import ConnectionManager
from app.core.websocket.handler import WebSocketHandler

# 移除 pytest_configure 函数，改用 pytest.ini 或直接在代码中设置
pytest_plugins = ["pytest_asyncio"]
pytestmark = pytest.mark.asyncio

# 设置 asyncio_mode
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as asyncio test"
    )

# 其余的 fixtures 保持不变
@pytest.fixture
def test_client():
    """创建测试客户端"""
    return TestClient(app)

# ... (其余代码保持不变)
@pytest.fixture
def test_client():
    """创建测试客户端"""
    return TestClient(app)

@pytest.fixture
def connection_manager():
    """创建连接管理器实例"""
    return ConnectionManager()

# 修改为异步 fixture
@pytest_asyncio.fixture
async def websocket_handler(connection_manager):
    """创建WebSocket处理器实例"""
    handler = WebSocketHandler(connection_manager)
    try:
        yield handler
    finally:
        await handler.close_all_connections()

@pytest.fixture
def processor():
    """创建FaceMesh处理器实例"""
    return EnhancedFaceMeshProcessor()

@pytest.fixture
def sample_image():
    """创建测试用图像"""
    # 创建一个简单的测试图像
    width, height = 640, 480
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 添加一些简单的图形，模拟人脸
    # 头部轮廓
    cv2.ellipse(image, 
                (width//2, height//2), 
                (100, 150), 
                0, 0, 360, 
                (255, 255, 255), 
                -1)
    
    # 眼睛
    cv2.circle(image, (width//2 - 40, height//2 - 20), 10, (0, 0, 0), -1)
    cv2.circle(image, (width//2 + 40, height//2 - 20), 10, (0, 0, 0), -1)
    
    # 鼻子
    cv2.rectangle(image, 
                 (width//2 - 10, height//2 - 10),
                 (width//2 + 10, height//2 + 20),
                 (0, 0, 0), 
                 -1)
    
    # 嘴巴
    cv2.ellipse(image, 
                (width//2, height//2 + 40), 
                (30, 10), 
                0, 0, 180, 
                (0, 0, 0), 
                -1)
    
    return image

@pytest.fixture
def mock_video_capture(sample_image):
    """模拟摄像头捕获"""
    class MockVideoCapture:
        def __init__(self):
            self.sample_image = sample_image
            self.is_opened = True

        def read(self):
            return True, self.sample_image.copy()

        def release(self):
            self.is_opened = False

        def isOpened(self):
            return self.is_opened

    return MockVideoCapture()

# 修改为异步 fixture
@pytest_asyncio.fixture
async def mock_websocket():
    """模拟WebSocket连接"""
    class MockWebSocket:
        async def accept(self):
            pass

        async def send_json(self, data):
            pass

        async def receive_text(self):
            return ""

        async def close(self):
            pass

    return MockWebSocket()