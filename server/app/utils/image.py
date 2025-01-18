import cv2
import numpy as np
import base64
from typing import Tuple, Optional

def encode_image_to_base64(image: np.ndarray) -> str:
    """将OpenCV图像转换为base64字符串"""
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def decode_base64_to_image(base64_string: str) -> np.ndarray:
    """将base64字符串转换为OpenCV图像"""
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def resize_image(image: np.ndarray, 
                max_width: Optional[int] = None, 
                max_height: Optional[int] = None) -> np.ndarray:
    """调整图像大小，保持纵横比"""
    if max_width is None and max_height is None:
        return image
        
    height, width = image.shape[:2]
    aspect_ratio = width / height

    if max_width and width > max_width:
        width = max_width
        height = int(width / aspect_ratio)
    
    if max_height and height > max_height:
        height = max_height
        width = int(height * aspect_ratio)
        
    return cv2.resize(image, (width, height))

def draw_metrics_on_image(image: np.ndarray, 
                         metrics: dict,
                         position: Tuple[int, int] = (10, 30),
                         font_scale: float = 0.6,
                         thickness: int = 2,
                         color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    """在图像上绘制指标数据"""
    img_with_text = image.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    y_offset = position[1]
    line_spacing = 25
    
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            text = f"{key}: {value:.2f}"
        else:
            text = f"{key}: {value}"
            
        cv2.putText(
            img_with_text,
            text,
            (position[0], y_offset),
            font,
            font_scale,
            color,
            thickness
        )
        y_offset += line_spacing
        
    return img_with_text

def enhance_image(image: np.ndarray, 
                 brightness: float = 1.0,
                 contrast: float = 1.0) -> np.ndarray:
    """调整图像的亮度和对比度"""
    enhanced = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
    return enhanced

def draw_landmarks(image: np.ndarray,
                  landmarks: list,
                  connections: list,
                  color: Tuple[int, int, int] = (0, 255, 0),
                  thickness: int = 1) -> np.ndarray:
    """在图像上绘制特征点和连接线"""
    img_with_landmarks = image.copy()
    height, width = image.shape[:2]
    
    # 绘制特征点
    for landmark in landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        cv2.circle(img_with_landmarks, (x, y), 2, color, thickness)
    
    # 绘制连接线
    for connection in connections:
        start_idx = connection[0]
        end_idx = connection[1]
        
        start_point = landmarks[start_idx]
        end_point = landmarks[end_idx]
        
        start_x = int(start_point.x * width)
        start_y = int(start_point.y * height)
        end_x = int(end_point.x * width)
        end_y = int(end_point.y * height)
        
        cv2.line(img_with_landmarks, 
                 (start_x, start_y), 
                 (end_x, end_y), 
                 color, 
                 thickness)
    
    return img_with_landmarks