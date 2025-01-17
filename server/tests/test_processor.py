import pytest
import cv2
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from app.core.facemesh.processor import EnhancedFaceMeshProcessor


@pytest.fixture
def processor():
    """初始化面部网格处理器用于测试"""
    return EnhancedFaceMeshProcessor()


@pytest.fixture
def sample_image():
    """创建一个简单的测试图像"""
    width = 640
    height = 480
    img = np.zeros((height, width, 3), dtype=np.uint8)
    return img


@pytest.fixture
def mock_landmarks():
    """创建模拟的面部特征点数据用于测试"""
    landmarks = []
    for i in range(468):  # MediaPipe Face Mesh 有468个特征点
        landmark = landmark_pb2.NormalizedLandmark()
        # 为偶数和奇数索引创建对称点
        if i % 2 == 0:
            landmark.x = 0.4
        else:
            landmark.x = 0.6
        landmark.y = 0.5
        landmarks.append(landmark)
    return landmarks


def test_processor_initialization(processor):
    """测试处理器初始化"""
    assert processor is not None
    assert processor.face_mesh is not None
    assert processor.drawing_utils is not None
    assert processor.drawing_spec is not None


def test_calculate_distance(processor):
    """测试两点之间距离计算"""
    # 创建测试点
    point1 = landmark_pb2.NormalizedLandmark()
    point1.x = 0.1
    point1.y = 0.1

    point2 = landmark_pb2.NormalizedLandmark()
    point2.x = 0.2
    point2.y = 0.2

    # 在100x100的图像中计算距离
    distance = processor.calculate_distance(point1, point2, 100, 100)
    expected_distance = np.sqrt(2) * 10  # 预期距离为10√2

    assert abs(distance - expected_distance) < 0.001


def test_calculate_angle(processor):
    """测试三点之间角度计算"""
    # 创建一个直角三角形
    point1 = (0, 0)
    point2 = (0, 1)
    point3 = (1, 1)

    angle = processor.calculate_angle(point1, point2, point3)
    assert abs(angle - 90) < 0.001  # 应该是90度角


def test_process_frame_with_empty_image(processor, sample_image):
    """测试处理空白图像"""
    processed_frame, metrics_list = processor.process_frame(sample_image)

    # 验证返回值
    assert isinstance(processed_frame, np.ndarray)
    assert isinstance(metrics_list, list)
    assert len(metrics_list) == 0  # 空白图像不应该检测到任何人脸


def test_face_shape_analysis(processor, mock_landmarks):
    """测试面部形状分析度量"""
    shape_metrics = processor.analyze_face_shape(mock_landmarks, 100, 100)

    # 验证返回的度量
    assert isinstance(shape_metrics, dict)
    expected_shapes = {'oval', 'round', 'square', 'heart', 'diamond'}
    assert set(shape_metrics.keys()) == expected_shapes

    # 验证分数范围
    for score in shape_metrics.values():
        assert 0 <= score <= 1


def test_symmetry_calculation(processor, mock_landmarks):
    """测试面部对称性计算"""
    symmetry_metrics = processor.calculate_symmetry(mock_landmarks, 100, 100)

    # 验证返回的度量
    assert isinstance(symmetry_metrics, dict)
    assert 'overall_symmetry' in symmetry_metrics

    # 对于完全对称的模拟数据，整体对称性应该很高
    assert symmetry_metrics['overall_symmetry'] > 0.9


def test_golden_ratio_calculation(processor, mock_landmarks):
    """测试黄金分割比例计算"""
    golden_metrics = processor.calculate_golden_ratio(mock_landmarks, 100, 100)

    # 验证返回的度量
    assert isinstance(golden_metrics, dict)
    expected_metrics = {
        'forehead_nose_ratio',  # 前额到鼻子的比例
        'nose_chin_ratio',      # 鼻子到下巴的比例
        'width_height_ratio',   # 宽高比
        'overall_golden_ratio'  # 整体黄金分割比
    }
    assert set(golden_metrics.keys()) == expected_metrics

    # 验证分数范围
    for score in golden_metrics.values():
        assert 0 <= score <= 1


def test_calculate_overall_score(processor):
    """测试整体评分计算"""
    # 创建模拟度量数据
    mock_metrics = {
        'symmetry': {'overall_symmetry': 0.9},              # 对称性
        'golden_ratio': {'overall_golden_ratio': 0.8},      # 黄金分割
        'face_shape': {'oval': 0.7, 'round': 0.6},         # 脸型
        'five_eye_metrics': 10.0,                          # 五眼
        'three_section_metrics': {                         # 三庭
            'Three_Section_Metric_A': 5.0,
            'Three_Section_Metric_B': 5.0,
            'Three_Section_Metric_C': 5.0
        },
        'da_vinci_ratio': 1.6,                            # 达芬奇比例
        'eye_angle_metrics': {                            # 眼角度量
            'EB_Metric_G': 45.0,
            'EB_Metric_H': 45.0
        }
    }

    score = processor.calculate_overall_score(mock_metrics)
    
    # 验证分数范围
    assert 0 <= score <= 100


if __name__ == '__main__':
    pytest.main([__file__])