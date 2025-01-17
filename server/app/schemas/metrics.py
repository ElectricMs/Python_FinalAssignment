from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class ThreeSectionMetrics(BaseModel):
    metric_a: float = Field(..., description="第一项三庭指标")
    metric_b: float = Field(..., description="第二项三庭指标")
    metric_c: float = Field(..., description="第三项三庭指标")

class EyeAngleMetrics(BaseModel):
    left_eye: float = Field(..., description="左眼角度")
    right_eye: float = Field(..., description="右眼角度")

class SymmetryMetrics(BaseModel):
    overall_symmetry: float = Field(..., description="整体对称性得分")
    feature_symmetry: Dict[str, float] = Field(..., description="各特征点对称性得分")

class GoldenRatioMetrics(BaseModel):
    overall_ratio: float = Field(..., description="整体黄金分割得分")
    feature_ratios: Dict[str, float] = Field(..., description="各特征黄金分割比例")

class FaceShapeMetrics(BaseModel):
    shape_type: str = Field(..., description="脸型类型")
    confidence: float = Field(..., description="置信度")
    shape_scores: Dict[str, float] = Field(..., description="各脸型的匹配得分")

class FacialMetrics(BaseModel):
    five_eye_metrics: Optional[float] = None
    three_section_metrics: Optional[Dict[str, float]] = None
    da_vinci_ratio: Optional[float] = None
    eye_angle_metrics: Optional[Dict[str, float]] = None
    symmetry_metrics: Optional[Dict[str, float]] = None
    golden_ratio_metrics: Optional[Dict[str, float]] = None
    face_shape_metrics: Optional[Dict[str, float]] = None
    overall_score: Optional[float] = None

class ProcessingResponse(BaseModel):
    status: str = Field(..., description="处理状态")
    image: Optional[str] = Field(None, description="Base64编码的图像")
    metrics: Optional[List[Dict[str, Any]]] = Field(None, description="面部特征分析结果")
    error: Optional[str] = Field(None, description="错误信息")

class WebSocketMessage(BaseModel):
    type: str = Field(..., description="消息类型")
    data: ProcessingResponse = Field(..., description="消息数据")