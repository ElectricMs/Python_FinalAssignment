import numpy as np
from typing import List, Dict, Tuple, Any
import mediapipe as mp

class FacialMetricsCalculator:
    """面部特征计算器类，包含各种面部指标的计算方法"""
    
    @staticmethod
    def calculate_distance(point1: Any,
                         point2: Any,
                         img_width: int,
                         img_height: int) -> float:
        """计算两点间的欧氏距离"""
        x1, y1 = point1.x * img_width, point1.y * img_height
        x2, y2 = point2.x * img_width, point2.y * img_height
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    @staticmethod
    def calculate_angle(point1: Tuple[float, float],
                       point2: Tuple[float, float],
                       point3: Tuple[float, float]) -> float:
        """计算三点形成的角度"""
        a = np.array(point1)
        b = np.array(point2)
        c = np.array(point3)
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        
        return np.degrees(angle)

    @classmethod
    def calculate_five_eye_metrics(cls,
                                 landmarks: List[Any],
                                 img_width: int,
                                 img_height: int) -> Dict[str, float]:
        """计算五眼指标"""
        # 获取关键点
        FL = landmarks[234]  # 脸轮廓最左点
        FR = landmarks[454]  # 脸轮廓最右点
        ELL = landmarks[33]  # 左眼左眼角
        ELR = landmarks[133]  # 左眼右眼角
        ERL = landmarks[362]  # 右眼左眼角
        ERR = landmarks[263]  # 右眼右眼角

        # 计算横向距离
        FL_X = FL.x * img_width
        FR_X = FR.x * img_width
        ELL_X = ELL.x * img_width
        ELR_X = ELR.x * img_width
        ERL_X = ERL.x * img_width
        ERR_X = ERR.x * img_width

        # 计算比例
        Left_Right = FR_X - FL_X
        Six_X = np.array([FL_X, ELL_X, ELR_X, ERL_X, ERR_X, FR_X])
        Five_Distance = 100 * np.diff(Six_X) / Left_Right
        
        return {
            "distances": Five_Distance.tolist(),
            "score": cls._calculate_five_eye_score(Five_Distance)
        }

    @staticmethod
    def _calculate_five_eye_score(distances: np.ndarray) -> float:
        """计算五眼得分"""
        ideal_ratios = np.array([1, 1, 1, 1, 1])  # 理想的五等分
        deviation = np.abs(distances - ideal_ratios)
        score = 100 * (1 - np.mean(deviation) / 100)
        return max(0, min(100, score))

    @classmethod
    def calculate_three_section_metrics(cls,
                                      landmarks: List[Any],
                                      img_height: int) -> Dict[str, float]:
        """计算三庭指标"""
        # 获取关键点
        FT = landmarks[10]   # 发际线
        MX = landmarks[9]    # 眉心
        NB = landmarks[2]    # 鼻翼下缘
        LC = landmarks[13]   # 嘴唇中心
        LB = landmarks[17]   # 嘴唇下缘
        FB = landmarks[152]  # 下巴

        # 计算纵向距离
        points_y = np.array([
            FT.y * img_height,
            MX.y * img_height,
            NB.y * img_height,
            LC.y * img_height,
            LB.y * img_height,
            FB.y * img_height
        ])
        
        distances = np.diff(points_y)
        total_height = FB.y * img_height - FT.y * img_height
        section_ratios = distances / total_height

        return {
            "ratios": section_ratios.tolist(),
            "score": cls._calculate_three_section_score(section_ratios)
        }

    @staticmethod
    def _calculate_three_section_score(ratios: np.ndarray) -> float:
        """计算三庭得分"""
        ideal_ratios = np.array([0.333, 0.333, 0.111, 0.111, 0.111])  # 理想的三庭比例
        deviation = np.abs(ratios - ideal_ratios)
        score = 100 * (1 - np.mean(deviation))
        return max(0, min(100, score))