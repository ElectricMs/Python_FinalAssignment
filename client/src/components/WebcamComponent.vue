<template>
    <div>
      <div v-if="imageSrc">
        <h2>实时画面</h2>
        <img :src="imageSrc" alt="Webcam Stream" />
      </div>
      <div v-if="results">
        <h2>实时分析结果</h2>
        <ul>
          <li v-for="(value, key) in results" :key="key">
            {{ key }}: {{ value }}
          </li>
        </ul>
      </div>
      <button @click="startWebSocket">开始实时打分</button>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        websocket: null, // WebSocket 实例
        imageSrc: null,  // 实时图像
        results: null,   // 分析结果
      };
    },
    methods: {
      startWebSocket() {
        // 建立 WebSocket 连接
        this.websocket = new WebSocket("ws://127.0.0.1:8000/ws");
  
        // 处理 WebSocket 消息
        this.websocket.onmessage = (event) => {
          const data = JSON.parse(event.data);
  
          if (data.image) {
            // 更新图像
            this.imageSrc = `data:image/jpeg;base64,${data.image}`;
          }
          if (data.results) {
            // 更新分析结果
            this.results = data.results;
          }
        };
  
        // 错误处理
        this.websocket.onerror = (error) => {
          console.error("WebSocket Error:", error);
          alert("连接失败，请检查后端服务是否启动！");
        };
  
        // 关闭连接
        this.websocket.onclose = () => {
          console.log("WebSocket connection closed");
          this.websocket = null;
        };
      },
    },
  };
  </script>
  
  <style>
  img {
    max-width: 600px;
    border: 2px solid #ccc;
    margin: 20px 0;
  }
  
  button {
    margin-top: 20px;
    padding: 10px 20px;
    font-size: 16px;
    background-color: #007bff;
    color: #fff;
    border: none;
    cursor: pointer;
    border-radius: 5px;
  }
  
  button:hover {
    background-color: #0056b3;
  }
  </style>
  