import numpy as np
import mediapipe as mp
from typing import List, Dict, Tuple, Any, Union

def initialize_face_mesh(
    static_image_mode: bool = False,
    max_num_faces: int = 5,
    min_detection_confidence: float = 0.5,
    min_tracking_confidence: float = 0.5
) -> Any:
    """初始化FaceMesh模型"""
    return mp.solutions.face_mesh.FaceMesh(
        static_image_mode=static_image_mode,
        max_num_faces=max_num_faces,
        refine_landmarks=True,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence
    )

def get_face_landmarks_dict(
    landmarks: Any
) -> Dict[str, List[int]]:
    """返回面部关键特征点的索引字典"""
    return {
        'face_oval': list(mp.solutions.face_mesh.FACEMESH_FACE_OVAL),
        'lips': list(mp.solutions.face_mesh.FACEMESH_LIPS),
        'left_eye': list(mp.solutions.face_mesh.FACEMESH_LEFT_EYE),
        'right_eye': list(mp.solutions.face_mesh.FACEMESH_RIGHT_EYE),
        'left_eyebrow': list(mp.solutions.face_mesh.FACEMESH_LEFT_EYEBROW),
        'right_eyebrow': list(mp.solutions.face_mesh.FACEMESH_RIGHT_EYEBROW),
        'nose': list(mp.solutions.face_mesh.FACEMESH_NOSE)
    }

def normalize_landmarks(
    landmarks: List[Any],
    image_width: int,
    image_height: int
) -> np.ndarray:
    """将特征点标准化为像素坐标"""
    normalized = np.array([[lm.x * image_width, lm.y * image_height, lm.z * image_width]
                          for lm in landmarks])
    return normalized

def calculate_face_center(
    landmarks: List[Any]
) -> Tuple[float, float]:
    """计算面部中心点"""
    x_coords = [landmark.x for landmark in landmarks]
    y_coords = [landmark.y for landmark in landmarks]
    return np.mean(x_coords), np.mean(y_coords)

def get_face_region_landmarks(
    landmarks: List[Any],
    region: str
) -> List[Any]:
    """获取指定面部区域的特征点"""
    landmark_dict = get_face_landmarks_dict(landmarks)
    if region not in landmark_dict:
        raise ValueError(f"Unknown region: {region}")
    
    indices = landmark_dict[region]
    return [landmarks[i] for i in indices]

def calculate_face_direction(
    landmarks: List[Any]
) -> Dict[str, float]:
    """计算面部朝向"""
    # 获取鼻尖和面部轮廓点
    nose_tip = landmarks[4]
    left_face = landmarks[234]
    right_face = landmarks[454]
    
    # 计算水平方向的偏转
    face_width = right_face.x - left_face.x
    nose_position = (nose_tip.x - left_face.x) / face_width - 0.5
    
    # 计算垂直方向的偏转
    vertical_angle = np.arctan2(nose_tip.z, nose_tip.y)
    
    return {
        "horizontal_offset": nose_position * 100,  # 转换为百分比
        "vertical_angle": np.degrees(vertical_angle)
    }

def check_face_visibility(
    landmarks: List[Any]
) -> Dict[str, bool]:
    """检查面部各区域的可见性"""
    landmark_dict = get_face_landmarks_dict(landmarks)
    visibility = {}
    
    for region, indices in landmark_dict.items():
        region_landmarks = [landmarks[i] for i in indices]
        # 如果区域的关键点z值平均值大于阈值，认为该区域可见
        avg_z = np.mean([lm.z for lm in region_landmarks])
        visibility[region] = avg_z > -0.1
        
    return visibility

def get_landmark_confidence(
    landmarks: List[Any]
) -> float:
    """获取特征点检测的置信度"""
    # 这里使用z坐标的方差作为置信度的指标
    z_coords = [landmark.z for landmark in landmarks]
    confidence = 1.0 / (1.0 + np.var(z_coords))
    return min(1.0, confidence)

def draw_landmarks_with_style(
    image: np.ndarray,
    landmarks: Any,
    drawing_spec: Dict[str, Any]
) -> np.ndarray:
    """使用自定义样式绘制特征点"""
    mp_drawing = mp.solutions.drawing_utils
    annotated_image = image.copy()
    
    # 绘制面部轮廓
    mp_drawing.draw_landmarks(
        image=annotated_image,
        landmark_list=landmarks,
        connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
        landmark_drawing_spec=drawing_spec.get('landmark_spec'),
        connection_drawing_spec=drawing_spec.get('connection_spec')
    )
    
    return annotated_image