import cv2
import numpy as np
import mediapipe as mp
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import base64

# 初始化 FastAPI 应用
app = FastAPI()

# 引入 FaceMeshProcessor 类
class FaceMeshProcessor:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            refine_landmarks=True,
            max_num_faces=5,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def process_frame(self, img: np.ndarray) -> dict:
        h, w = img.shape[:2]
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)

        if not results.multi_face_landmarks:
            return {"message": "No face detected"}

        face_metrics = []
        for face_landmarks in results.multi_face_landmarks:
            metrics = self.calculate_metrics(face_landmarks, h, w)
            face_metrics.append(metrics)

        return {"face_count": len(face_metrics), "face_metrics": face_metrics}

    def calculate_metrics(self, face_landmarks, h, w):
        # 简化版：五眼比例、三庭比例、达芬奇比例
        metrics = {}
        landmarks = face_landmarks.landmark

        # 五眼比例计算
        FL, FR = landmarks[234], landmarks[454]
        FL_X, FR_X = int(FL.x * w), int(FR.x * w)
        metrics["Five_Eye_Metrics"] = FR_X - FL_X

        # 达芬奇比例
        LL, LR, NL, NR = landmarks[61], landmarks[291], landmarks[129], landmarks[358]
        metrics["Da_Vinci"] = (LR.x - LL.x) / (NR.x - NL.x)

        return metrics

# 实例化人脸处理类
processor = FaceMeshProcessor()

# WebSocket 路由
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        await websocket.send_json({"error": "Cannot access webcam"})
        await websocket.close()
        return

    try:
        while True:
            # 读取摄像头帧
            ret, frame = cap.read()
            if not ret:
                await websocket.send_json({"error": "Failed to capture frame"})
                break

            # 处理图像
            results = processor.process_frame(frame)

            # 在帧上绘制结果
            for face in results.get("face_metrics", []):
                cv2.putText(frame, f"Da Vinci: {face['Da_Vinci']:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # 将图像转换为 base64 格式发送到前端
            _, buffer = cv2.imencode(".jpg", frame)
            frame_base64 = base64.b64encode(buffer).decode("utf-8")
            await websocket.send_json({"image": frame_base64, "results": results})

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        cap.release()
