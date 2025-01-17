import numpy as np
import mediapipe as mp
import cv2
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

# 数据类用于存储面部指标


@dataclass
class FacialMetrics:
    five_eye_metrics: float
    three_section_metrics: Dict[str, float]
    da_vinci_ratio: float
    eye_angle_metrics: Dict[str, float]
    symmetry_metrics: Dict[str, float]
    golden_ratio_metrics: Dict[str, float]
    face_shape_metrics: Dict[str, float]
    overall_score: float


class EnhancedFaceMeshProcessor:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            refine_landmarks=True,
            max_num_faces=5,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.drawing_utils = mp.solutions.drawing_utils
        self.drawing_spec = self.drawing_utils.DrawingSpec(
            thickness=1, circle_radius=1, color=(66, 77, 229)
        )

    def calculate_distance(self, point1: Any, point2: Any,
                         img_width: int, img_height: int) -> float:
        """计算两点间的欧氏距离"""
        x1, y1 = point1.x * img_width, point1.y * img_height
        x2, y2 = point2.x * img_width, point2.y * img_height
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def calculate_angle(self, point1: Tuple[float, float],
                       point2: Tuple[float, float],
                       point3: Tuple[float, float]) -> float:
        """计算三点形成的角度"""
        a = np.array(point1)
        b = np.array(point2)
        c = np.array(point3)

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / \
                              (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)

        return np.degrees(angle)

    def calculate_symmetry(self, landmarks: List[Any],
                         img_width: int,
                         img_height: int) -> Dict[str, float]:
        """计算面部对称性指标"""
        symmetry_pairs = [
            (33, 263),  # 左右眼外角
            (133, 362),  # 左右眼内角
            (70, 300),  # 左右眉毛外端
            (105, 334),  # 左右眉毛内端
            (61, 291),  # 嘴角
            (234, 454),  # 脸颊最宽处
            (58, 288),   # 下颌角
        ]

        nose_bridge = landmarks[168]
        chin = landmarks[152]
        midline_angle = np.arctan2(
    chin.y - nose_bridge.y,
     chin.x - nose_bridge.x)

        symmetry_scores = {}

        for left_idx, right_idx in symmetry_pairs:
            left_point = landmarks[left_idx]
            right_point = landmarks[right_idx]

            left_dist = self.calculate_distance(
    left_point, nose_bridge, img_width, img_height)
            right_dist = self.calculate_distance(
    right_point, nose_bridge, img_width, img_height)

            symmetry_score = 1 - \
                abs(left_dist - right_dist) / max(left_dist, right_dist)
            symmetry_scores[f'symmetry_{left_idx}_{right_idx}'] = symmetry_score

        overall_symmetry = np.mean(list(symmetry_scores.values()))
        symmetry_scores['overall_symmetry'] = overall_symmetry

        return symmetry_scores

    def calculate_golden_ratio(self, landmarks: List[Any],
                             img_width: int,
                             img_height: int) -> Dict[str, float]:
        """计算面部黄金分割比例"""
        GOLDEN_RATIO = 1.618

        hairline = landmarks[10]
        brow_center = landmarks[151]
        nose_tip = landmarks[4]
        chin = landmarks[152]
        left_temple = landmarks[234]
        right_temple = landmarks[454]

        forehead_height = self.calculate_distance(
    hairline, brow_center, img_width, img_height)
        brow_to_nose = self.calculate_distance(
    brow_center, nose_tip, img_width, img_height)
        nose_to_chin = self.calculate_distance(
            nose_tip, chin, img_width, img_height)
        face_width = self.calculate_distance(
    left_temple, right_temple, img_width, img_height)
        face_height = self.calculate_distance(
            hairline, chin, img_width, img_height)

        golden_ratios = {
            'forehead_nose_ratio': forehead_height / brow_to_nose,
            'nose_chin_ratio': brow_to_nose / nose_to_chin,
            'width_height_ratio': face_width / face_height,
        }

        golden_scores = {
            k: 1 - min(abs(v - GOLDEN_RATIO) / GOLDEN_RATIO, 1)
            for k, v in golden_ratios.items()
        }

        golden_scores['overall_golden_ratio'] = np.mean(
            list(golden_scores.values()))

        return golden_scores

    def analyze_face_shape(self, landmarks: List[Any],
                          img_width: int,
                          img_height: int) -> Dict[str, float]:
        """分析脸型特征"""
        chin = landmarks[152]
        left_cheek = landmarks[234]
        right_cheek = landmarks[454]
        left_jaw = landmarks[58]
        right_jaw = landmarks[288]
        forehead = landmarks[10]

        face_width = self.calculate_distance(
    left_cheek, right_cheek, img_width, img_height)
        face_height = self.calculate_distance(
            forehead, chin, img_width, img_height)
        jaw_width = self.calculate_distance(
    left_jaw, right_jaw, img_width, img_height)

        left_jaw_angle = self.calculate_angle(
            (left_cheek.x * img_width, left_cheek.y * img_height),
            (left_jaw.x * img_width, left_jaw.y * img_height),
            (chin.x * img_width, chin.y * img_height)
        )
        right_jaw_angle = self.calculate_angle(
            (right_cheek.x * img_width, right_cheek.y * img_height),
            (right_jaw.x * img_width, right_jaw.y * img_height),
            (chin.x * img_width, chin.y * img_height)
        )

        shape_metrics = {
            'width_height_ratio': face_width / face_height,
            'jaw_width_ratio': jaw_width / face_width,
            'left_jaw_angle': left_jaw_angle,
            'right_jaw_angle': right_jaw_angle,
        }

        shape_scores = {
            'oval': self._calculate_oval_score(shape_metrics),
            'round': self._calculate_round_score(shape_metrics),
            'square': self._calculate_square_score(shape_metrics),
            'heart': self._calculate_heart_score(shape_metrics),
            'diamond': self._calculate_diamond_score(shape_metrics)
        }

        return shape_scores

    # ... 保留其他计算脸型分数的辅助方法 (_calculate_*_score) ...
    def _calculate_oval_score(self, metrics: Dict[str, float]) -> float:
        """计算椭圆形脸的匹配度"""
        ideal_ratio = 1.5
        ratio_score = 1 - \
            min(abs(metrics['width_height_ratio'] -
                ideal_ratio) / ideal_ratio, 1)
        jaw_score = 1 - abs(metrics['jaw_width_ratio'] - 0.8)
        return (ratio_score + jaw_score) / 2

    def _calculate_round_score(self, metrics: Dict[str, float]) -> float:
        """计算圆形脸的匹配度"""
        ratio_score = 1 - min(abs(metrics['width_height_ratio'] - 1) / 0.5, 1)
        return ratio_score

    def _calculate_square_score(self, metrics: Dict[str, float]) -> float:
        """计算方形脸的匹配度"""
        angle_score = np.mean([
            1 if 80 <= angle <= 100 else 1 - min(abs(angle - 90) / 45, 1)
            for angle in [metrics['left_jaw_angle'], metrics['right_jaw_angle']]
        ])
        jaw_score = 1 - abs(metrics['jaw_width_ratio'] - 0.9)
        return (angle_score + jaw_score) / 2

    def _calculate_heart_score(self, metrics: Dict[str, float]) -> float:
        """计算心形脸的匹配度"""
        jaw_score = 1 - abs(metrics['jaw_width_ratio'] - 0.7)
        return jaw_score

    def _calculate_diamond_score(self, metrics: Dict[str, float]) -> float:
        """计算钻石形脸的匹配度"""
        angle_score = np.mean([
            1 if 110 <= angle <= 130 else 1 - min(abs(angle - 120) / 45, 1)
            for angle in [metrics['left_jaw_angle'], metrics['right_jaw_angle']]
        ])
        return angle_score

    def calculate_overall_score(
        self, metrics: Dict[str, Dict[str, float]]) -> float:
        """计算综合评分"""
        weights = {
            'symmetry': 0.25,
            'golden_ratio': 0.25,
            'face_shape': 0.2,
            'five_eye': 0.1,
            'three_section': 0.1,
            'da_vinci': 0.05,
            'eye_angle': 0.05
        }

        scores = {
            'symmetry': metrics['symmetry']['overall_symmetry'],
            'golden_ratio': metrics['golden_ratio']['overall_golden_ratio'],
            'face_shape': max(metrics['face_shape'].values()),
            'five_eye': 1 - min(metrics['five_eye_metrics'] / 100, 1),
            'three_section': 1 - np.mean([
                metrics['three_section_metrics'][key] for key in
                ['Three_Section_Metric_A',
    'Three_Section_Metric_B',
     'Three_Section_Metric_C']
            ]) / 100,
            'da_vinci': 1 - min(abs(metrics['da_vinci_ratio'] - 1.618) / 1.618, 1),
            'eye_angle': 1 - np.mean([
                abs(metrics['eye_angle_metrics'][key] - 49) / 49 for key in
                ['EB_Metric_G', 'EB_Metric_H']
            ])
        }

        weighted_score = sum(scores[k] * weights[k] for k in weights)
        final_score = 100 * (weighted_score ** 0.5)

        return min(100, max(0, final_score))

    def process_frame(
        self, img: np.ndarray) -> Tuple[np.ndarray, List[FacialMetrics]]:
        """处理每一帧图像"""
        h, w = img.shape[:2]
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)

        metrics_list = []
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.drawing_utils.draw_landmarks(
                    image=img,
                    landmark_list=face_landmarks,
                    connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=self.drawing_spec,
                    connection_drawing_spec=self.drawing_spec,
                )

                basic_metrics = self.calculate_basic_metrics(
                    face_landmarks.landmark, h, w)
                symmetry_metrics = self.calculate_symmetry(
                    face_landmarks.landmark, w, h)
                golden_ratio_metrics = self.calculate_golden_ratio(
                    face_landmarks.landmark, w, h)
                face_shape_metrics = self.analyze_face_shape(
                    face_landmarks.landmark, w, h)

                all_metrics = {
                    'five_eye_metrics': basic_metrics['Five_Eye_Metrics'],
                    'three_section_metrics': {
                        'Three_Section_Metric_A': basic_metrics['Three_Section_Metric_A'],
                        'Three_Section_Metric_B': basic_metrics['Three_Section_Metric_B'],
                        'Three_Section_Metric_C': basic_metrics['Three_Section_Metric_C']
                    },
                    'da_vinci_ratio': basic_metrics['Da_Vinci'],
                    'eye_angle_metrics': {
                        'EB_Metric_G': basic_metrics['EB_Metric_G'],
                        'EB_Metric_H': basic_metrics['EB_Metric_H']
                    },
                    'symmetry': symmetry_metrics,
                    'golden_ratio': golden_ratio_metrics,
                    'face_shape': face_shape_metrics
                }

                overall_score = self.calculate_overall_score(all_metrics)

                facial_metrics = FacialMetrics(
                    five_eye_metrics=basic_metrics['Five_Eye_Metrics'],
                    three_section_metrics=all_metrics['three_section_metrics'],
                    da_vinci_ratio=basic_metrics['Da_Vinci'],
                    eye_angle_metrics=all_metrics['eye_angle_metrics'],
                    symmetry_metrics=symmetry_metrics,
                    golden_ratio_metrics=golden_ratio_metrics,
                    face_shape_metrics=face_shape_metrics,
                    overall_score=overall_score
                )

                metrics_list.append(facial_metrics)
                #self.display_metrics(img, facial_metrics)

        return img, metrics_list


    def calculate_basic_metrics(
        self, landmarks: List[Any], h: int, w: int) -> Dict[str, float]:
            """计算基础指标（五眼、三庭、达芬奇比例等）"""
            metrics = {}

            # ====== 五眼相关计算 ======
            FL = landmarks[234]  # 脸轮廓最左点
            FR = landmarks[454]  # 脸轮廓最右点
            ELL = landmarks[33]  # 左眼左眼角
            ELR = landmarks[133]  # 左眼右眼角
            ERL = landmarks[362]  # 右眼左眼角
            ERR = landmarks[263]  # 右眼右眼角

            FL_X, FR_X = FL.x * w, FR.x * w
            ELL_X, ELR_X = ELL.x * w, ELR.x * w
            ERL_X, ERR_X = ERL.x * w, ERR.x * w

            Left_Right = FR_X - FL_X
            Six_X = np.array([FL_X, ELL_X, ELR_X, ERL_X, ERR_X, FR_X])
            Five_Distance = 100 * np.diff(Six_X) / Left_Right
            Eye_Width_Mean = np.mean([Five_Distance[1], Five_Distance[3]])
            Five_Eye_Diff = Five_Distance - Eye_Width_Mean
            metrics['Five_Eye_Metrics'] = np.linalg.norm(Five_Eye_Diff)

            # ====== 三庭相关计算 ======
            FT = landmarks[10]  # 发际线
            MX = landmarks[9]   # 眉心
            NB = landmarks[2]   # 鼻翼下缘
            LC = landmarks[13]  # 嘴唇中心
            LB = landmarks[17]  # 嘴唇下缘
            FB = landmarks[152]  # 下巴

            FT_Y = FT.y * h
            MX_Y = MX.y * h
            NB_Y = NB.y * h
            LC_Y = LC.y * h
            LB_Y = LB.y * h
            FB_Y = FB.y * h

            Top_Down = FB_Y - FT_Y
            Six_Y = np.array([FT_Y, MX_Y, NB_Y, LC_Y, LB_Y, FB_Y])
            Three_Section_Distance = 100 * np.diff(Six_Y) / Top_Down

            metrics['Three_Section_Metric_A'] = np.abs(
                Three_Section_Distance[1] - sum(Three_Section_Distance[2:]))
            metrics['Three_Section_Metric_B'] = np.abs(
                Three_Section_Distance[2] - sum(Three_Section_Distance[2:]) / 3)
            metrics['Three_Section_Metric_C'] = np.abs(
                sum(Three_Section_Distance[3:]) - sum(Three_Section_Distance[2:]) / 2)

            # ====== 达芬奇比例计算 ======
            LL = landmarks[61]   # 嘴唇左角
            LR = landmarks[291]  # 嘴唇右角
            NL = landmarks[129]  # 鼻子左缘
            NR = landmarks[358]  # 鼻子右缘
            metrics['Da_Vinci'] = (LR.x - LL.x) / (NR.x - NL.x)

            # ====== 内眼角开合度计算 ======
            ELRT = landmarks[157]  # 左内眼角上点
            ELRB = landmarks[154]  # 左内眼角下点
            ERLT = landmarks[384]  # 右内眼角上点
            ERRB = landmarks[381]  # 右内眼角下点

            # 计算左眼角度
            vector_a = np.array([ELRT.x - ELR.x, ELRT.y - ELR.y])
            vector_b = np.array([ELRB.x - ELR.x, ELRB.y - ELR.y])
            cos = vector_a.dot(vector_b) / \
                            (np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
            metrics['EB_Metric_G'] = np.degrees(np.arccos(cos))

            # 计算右眼角度
            vector_a = np.array([ERLT.x - ERL.x, ERLT.y - ERL.y])
            vector_b = np.array([ERRB.x - ERL.x, ERRB.y - ERL.y])
            cos = vector_a.dot(vector_b) / \
                            (np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
            metrics['EB_Metric_H'] = np.degrees(np.arccos(cos))

            return metrics

    def display_metrics(self, img: np.ndarray, metrics: FacialMetrics) -> None:
        """在图像上显示分析结果"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        padding = 10
        line_height = 25
        
        # 显示总分
        cv2.putText(
            img,
            f"Overall Score: {metrics.overall_score:.1f}",
            (padding, 30),
            font,
            font_scale,
            (0, 255, 0),
            thickness
        )
        
        # 显示主要分类得分
        y_offset = 60
        for category, score in [
            ("Symmetry", metrics.symmetry_metrics['overall_symmetry']),
            ("Golden Ratio", metrics.golden_ratio_metrics['overall_golden_ratio']),
            ("Face Shape", max(metrics.face_shape_metrics.values()))
        ]:
            cv2.putText(
                img,
                f"{category}: {score:.2f}",
                (padding, y_offset),
                font,
                font_scale,
                (0, 255, 0),
                thickness
            )
            y_offset += line_height
        
        # 显示最匹配的脸型
        best_shape = max(metrics.face_shape_metrics.items(), key=lambda x: x[1])
        cv2.putText(
            img,
            f"Face Shape: {best_shape[0].title()} ({best_shape[1]:.2f})",
            (padding, y_offset),
            font,
            font_scale,
            (0, 255, 0),
            thickness
        )