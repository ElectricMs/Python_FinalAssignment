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
        # 五眼和三庭指标计算
        metrics = {}
        landmarks = face_landmarks.landmark

        # 五眼相关点
        FL = landmarks[234]
        FR = landmarks[454]
        ELL = landmarks[33]
        ELR = landmarks[133]
        ERL = landmarks[362]
        ERR = landmarks[263]

        FL_X, FR_X = int(FL.x * w), int(FR.x * w)
        ELL_X, ELR_X, ERL_X, ERR_X = int(ELL.x * w), int(ELR.x * w), int(ERL.x * w), int(ERR.x * w)

        Left_Right = FR_X - FL_X
        Five_Distance = 100 * np.diff([FL_X, ELL_X, ELR_X, ERL_X, ERR_X, FR_X]) / Left_Right
        Eye_Width_Mean = np.mean([Five_Distance[1], Five_Distance[3]])
        Five_Eye_Diff = Five_Distance - Eye_Width_Mean
        metrics['Five_Eye_Metrics'] = np.linalg.norm(Five_Eye_Diff)

        # 三庭相关点
        FT = landmarks[10]
        MX = landmarks[9]
        NB = landmarks[2]
        LC = landmarks[13]
        LB = landmarks[17]
        FB = landmarks[152]

        FT_Y, MX_Y, NB_Y, LC_Y, LB_Y, FB_Y = (
            int(FT.y * h), int(MX.y * h), int(NB.y * h),
            int(LC.y * h), int(LB.y * h), int(FB.y * h)
        )

        Top_Down = FB_Y - FT_Y
        Three_Section_Distance = 100 * np.diff([FT_Y, MX_Y, NB_Y, LC_Y, LB_Y, FB_Y]) / Top_Down
        metrics['Three_Section_Metric_A'] = abs(Three_Section_Distance[1] - sum(Three_Section_Distance[2:]))
        metrics['Three_Section_Metric_B'] = abs(Three_Section_Distance[2] - sum(Three_Section_Distance[2:]) / 3)
        metrics['Three_Section_Metric_C'] = abs(sum(Three_Section_Distance[3:]) - sum(Three_Section_Distance[2:]) / 2)

        # 达芬奇比例
        LL = landmarks[61]
        LR = landmarks[291]
        NL = landmarks[129]
        NR = landmarks[358]

        metrics['Da_Vinci'] = (LR.x - LL.x) / (NR.x - NL.x)

        # 内眼角开合度
        ELRT = landmarks[157]
        ELRB = landmarks[154]
        ERLT = landmarks[384]
        ERRB = landmarks[381]

        vector_a = np.array([ELRT.x - ELL.x, ELRT.y - ELL.y])
        vector_b = np.array([ELRB.x - ELL.x, ELRB.y - ELL.y])
        metrics['EB_Metric_G'] = np.degrees(np.arccos(np.clip(np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b)), -1.0, 1.0)))

        vector_a = np.array([ERLT.x - ERL.x, ERLT.y - ERL.y])
        vector_b = np.array([ERRB.x - ERL.x, ERRB.y - ERL.y])
        metrics['EB_Metric_H'] = np.degrees(np.arccos(np.clip(np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b)), -1.0, 1.0)))

        # 综合颜值评分
        metrics['Overall_Score'] = self.calculate_overall_score(metrics)

        return metrics


    def calculate_overall_score(self, metrics):
        # 简单加权评分模型（可调整权重）
        weights = {
            'Five_Eye_Metrics': -1,  # 越小越好
            'Three_Section_Metric_A': -1,
            'Three_Section_Metric_B': -1,
            'Three_Section_Metric_C': -1,
            'Da_Vinci': 1.,  # 越接近黄金比例越好
            'EB_Metric_G': -0.8,  # 角度越接近理想值越好
            'EB_Metric_H': -0.8
        }
        ideal_values = {
            'Da_Vinci': 1.5,  # 理想达芬奇比例
            'EB_Metric_G': 50,  # 理想角度
            'EB_Metric_H': 50
        }

        score = 0
        for key, weight in weights.items():
            value = metrics.get(key, 0)
            ideal = ideal_values.get(key, 0)
            if weight > 0:
                score += weight * max(0, (1 - abs(value - ideal) / ideal) * 100)
            else:
                score += weight * max(0, (1 - value / ideal) * 100)

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
