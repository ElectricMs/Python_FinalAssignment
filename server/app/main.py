from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.endpoints import websocket
from fastapi.responses import HTMLResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(websocket.router, prefix=settings.API_V1_STR)

# 测试页面路由
@app.get("/", response_class=HTMLResponse)
async def get():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>FaceMesh Analysis Test</title>
            <style>
                .container {
                    display: flex;
                    justify-content: space-between;
                    padding: 20px;
                }
                .video-container {
                    flex: 1;
                    margin-right: 20px;
                }
                .metrics-container {
                    flex: 1;
                    font-family: monospace;
                    white-space: pre-wrap;
                }
                img {
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="video-container">
                    <img id="video-feed" src="">
                </div>
                <div class="metrics-container">
                    <pre id="metrics"></pre>
                </div>
            </div>
            <script>
                const clientId = Date.now().toString();
                const ws = new WebSocket(`ws://${window.location.host}${settings.API_V1_STR}/ws/${clientId}`);
                const videoFeed = document.getElementById('video-feed');
                const metricsDisplay = document.getElementById('metrics');

                ws.onmessage = function(event) {
                    const message = JSON.parse(event.data);
                    const data = message.data;
                    
                    if (data.status === 'success') {
                        videoFeed.src = `data:image/jpeg;base64,${data.image}`;
                        metricsDisplay.textContent = JSON.stringify(data.metrics, null, 2);
                    } else {
                        metricsDisplay.textContent = `Error: ${data.error}`;
                    }
                };

                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };

                ws.onclose = function() {
                    console.log('WebSocket connection closed');
                };
            </script>
        </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)