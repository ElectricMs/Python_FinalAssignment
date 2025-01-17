import cv2
import asyncio
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket.manager import ConnectionManager
from app.schemas.metrics import ProcessingResponse
from app.config import settings
from app.utils.image import encode_image_to_base64
from app.schemas.metrics import FacialMetrics

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    try:
        # 建立连接
        await manager.connect(websocket, client_id)
        processor = manager.get_processor(client_id)
        
        # 初始化摄像头
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            await manager.send_message(
                client_id,
                ProcessingResponse(
                    status="error",
                    error="Cannot access webcam"
                )
            )
            return

        try:
            while True:
                # 处理视频帧
                ret, frame = cap.read() 
                if not ret:
                    break

                # 处理帧
                processed_frame, metrics = processor.process_frame(frame)

                # 确保 metrics 是列表
                if not isinstance(metrics, list):
                    metrics = [metrics]

                # 转换 metrics 为字典列表
                metrics_dict_list = []
                for metric in metrics:
                    print(f"处理 metric: {metric}")  # 调试打印
                    print(f"metric 类型: {type(metric)}")  # 调试打印
                    
                    try:
                        # 直接从 Pydantic 模型创建字典
                        if isinstance(metric, FacialMetrics):
                            metric_dict = metric.model_dump(exclude_none=True)
                        else:
                            # 构造符合 FacialMetrics 结构的数据
                            structured_metric = {
                                "five_eye_metrics": metric.five_eye_metrics if hasattr(metric, 'five_eye_metrics') else None,
                                "three_section_metrics": metric.three_section_metrics if hasattr(metric, 'three_section_metrics') else None,
                                "da_vinci_ratio": metric.da_vinci_ratio if hasattr(metric, 'da_vinci_ratio') else None,
                                "eye_angle_metrics": metric.eye_angle_metrics if hasattr(metric, 'eye_angle_metrics') else None,
                                "symmetry_metrics": metric.symmetry_metrics if hasattr(metric, 'symmetry_metrics') else None,
                                "golden_ratio_metrics": metric.golden_ratio_metrics if hasattr(metric, 'golden_ratio_metrics') else None,
                                "face_shape_metrics": metric.face_shape_metrics if hasattr(metric, 'face_shape_metrics') else None,
                                "overall_score": metric.overall_score if hasattr(metric, 'overall_score') else None
                            }
                            
                            # 移除为 None 的键
                            structured_metric = {k: v for k, v in structured_metric.items() if v is not None}
                            
                            facial_metrics = FacialMetrics.model_validate(structured_metric)
                            metric_dict = facial_metrics.model_dump(exclude_none=True)
                            
                        metrics_dict_list.append(metric_dict)
                        
                    except Exception as e:
                        print(f"处理 metrics 时出错: {e}")
                        continue

                # 创建响应
                response = ProcessingResponse(
                    status="success",
                    image=encode_image_to_base64(processed_frame),
                    metrics=metrics_dict_list
                )

                # 发送响应
                await manager.send_message(client_id, response)
                
                # 控制帧率
                await asyncio.sleep(settings.FRAME_INTERVAL)

        finally:
            cap.release()

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        
    except Exception as e:
        await manager.send_message(
            client_id,
            ProcessingResponse(
                status="error",
                error=str(e)
            )
        )
        manager.disconnect(client_id)