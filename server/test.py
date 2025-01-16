from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import cv2
import numpy as np
import mediapipe as mp
import base64
import json
import time

app = FastAPI()

mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=False,
    refine_landmarks=True,
    max_num_faces=5,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(66, 77, 229))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                # 接收数据并解码
                data = await websocket.receive_text()
                frame_data = json.loads(data).get("image")
                frame = decode_image(frame_data)

                # 处理图像
                start_time = time.time()
                processed_frame, metrics = process_frame(frame)
                processing_time = time.time() - start_time
                print(f"Processed a frame in {processing_time:.2f} seconds")

                # 返回数据
                _, buffer = cv2.imencode('.jpg', processed_frame)
                encoded_frame = base64.b64encode(buffer).decode('utf-8')
                await websocket.send_json({
                    "image": encoded_frame,
                    "metrics": {k: round(v, 2) for k, v in metrics.items()}
                })
            except Exception as e:
                print(f"Error processing frame: {e}")
                await websocket.send_json({"error": str(e)})
    except WebSocketDisconnect:
        print("WebSocket disconnected")


def decode_image(base64_string):
    img_data = base64.b64decode(base64_string)
    np_data = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
    return img


def process_frame(frame):
    h, w = frame.shape[:2]
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_face_mesh.process(img_rgb)
    metrics = {}

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # 绘制面部关键点
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec
            )
            metrics.update(calculate_metrics(face_landmarks, h, w))

    return frame, metrics


def calculate_metrics(face_landmarks, h, w):
    metrics = {}
    landmarks = face_landmarks.landmark

    # 计算面部宽度和高度
    left_cheek = landmarks[234]
    right_cheek = landmarks[454]
    chin = landmarks[152]
    forehead = landmarks[10]

    face_width = np.sqrt((right_cheek.x - left_cheek.x)**2 + (right_cheek.y - left_cheek.y)**2) * w
    face_height = np.sqrt((chin.y - forehead.y)**2 + (chin.x - forehead.x)**2) * h
    metrics['Face_Width'] = face_width
    metrics['Face_Height'] = face_height
    metrics['Face_Aspect_Ratio'] = face_width / face_height

    # 对称性度量
    left_eye = ((landmarks[33].x + landmarks[133].x) / 2, (landmarks[33].y + landmarks[133].y) / 2)
    right_eye = ((landmarks[362].x + landmarks[263].x) / 2, (landmarks[362].y + landmarks[263].y) / 2)
    nose_tip = (landmarks[1].x, landmarks[1].y)

    symmetry = abs(left_eye[0] - nose_tip[0]) - abs(right_eye[0] - nose_tip[0])
    metrics['Symmetry'] = symmetry

    return metrics


@app.get("/")
async def get():
    return HTMLResponse('<h1>WebSocket API Running</h1>')
