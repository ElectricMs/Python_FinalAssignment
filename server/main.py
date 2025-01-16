import cv2
import numpy as np
import mediapipe as mp
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import base64
import time

# 初始化 FastAPI 应用
app = FastAPI()

# FaceMeshProcessor 类
class FaceMeshProcessor:
    def __init__(self):
        # 初始化 Mediapipe FaceMesh
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

    def process_frame(self, img):
        h, w = img.shape[:2]
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)

        metrics_list = []
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 绘制特征点
                self.drawing_utils.draw_landmarks(
                    image=img,
                    landmark_list=face_landmarks,
                    connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=self.drawing_spec,
                    connection_drawing_spec=self.drawing_spec,
                )
                metrics = self.calculate_metrics(face_landmarks, h, w)
                metrics_list.append(metrics)
                self.display_metrics(img, metrics)

        return img, metrics_list

    def calculate_metrics(self, face_landmarks, h, w):
        # 人脸美学指标计算
        metrics = {}
        landmarks = face_landmarks.landmark

        # 五眼相关点
        FL = landmarks[234]
        FR = landmarks[454]
        FL_X, FR_X = int(FL.x * w), int(FR.x * w)
        metrics["Five_Eye_Metrics"] = FR_X - FL_X

        # 三庭比例计算
        FT = landmarks[10]
        NB = landmarks[9]
        MX = landmarks[152]
        metrics["Three_Section_Top"] = abs(NB.y - FT.y) / abs(MX.y - FT.y)
        metrics["Three_Section_Bottom"] = abs(MX.y - NB.y) / abs(MX.y - FT.y)

        # 达芬奇比例
        LL = landmarks[61]
        LR = landmarks[291]
        NL = landmarks[129]
        NR = landmarks[358]
        metrics["Da_Vinci"] = (LR.x - LL.x) / (NR.x - NL.x)

        # 综合评分（基于理想比例）
        metrics["Overall_Score"] = self.calculate_overall_score(metrics)
        return metrics

    def calculate_overall_score(self, metrics):
        # 简单加权评分模型
        weights = {
            "Five_Eye_Metrics": -1,
            "Three_Section_Top": 1,
            "Three_Section_Bottom": 1,
            "Da_Vinci": 1.5,
        }
        ideal_values = {
            "Five_Eye_Metrics": 1,
            "Three_Section_Top": 1,
            "Three_Section_Bottom": 1,
            "Da_Vinci": 1.618,
        }

        score = 0
        for key, weight in weights.items():
            value = metrics.get(key, 0)
            ideal = ideal_values.get(key, 1)
            score += weight * max(0, 100 - abs(value - ideal) * 100)
        return max(0, score)

    def display_metrics(self, img, metrics):
        y_offset = 30
        for key, value in metrics.items():
            text = f"{key}: {value:.2f}"
            cv2.putText(
                img, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )
            y_offset += 25

# 实例化 FaceMeshProcessor
processor = FaceMeshProcessor()

# WebSocket 路由
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        await websocket.send_json({"error": "Cannot access webcam"})
        await websocket.close()
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                await websocket.send_json({"error": "Failed to capture frame"})
                break

            processed_frame, results = processor.process_frame(frame)

            # 将图像转换为 base64 格式
            _, buffer = cv2.imencode(".jpg", processed_frame)
            frame_base64 = base64.b64encode(buffer).decode("utf-8")
            await websocket.send_json({"image": frame_base64, "results": results})

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        cap.release()
