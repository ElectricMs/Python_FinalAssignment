<template>
  <div>
    <div v-if="imageSrc">
      <h2>实时画面</h2>
      <img :src="imageSrc" alt="Webcam Stream" />
    </div>

    <div v-if="results">
      <h2>实时分析结果</h2>
      <ul>
        <li>
          <strong>五眼指标：</strong>
          {{ results[0].Five_Eye_Metrics || '数据缺失' }} (五眼比例)
          <p>描述：五眼比例计算的是面部两眼之间的比例，较小值通常表示对称性较好。</p>
        </li>
        <li>
          <strong>三庭比例：</strong>
          <ul>
            <li>上庭比例: {{ results[0].Three_Section_Top || '数据缺失' }}%</li>
            <li>下庭比例: {{ results[0].Three_Section_Bottom || '数据缺失' }}%</li>
          </ul>
          <p>描述：三庭比例表示面部上下部分的比例，理想的比例通常为对称。</p>
        </li>
        <li>
          <strong>达芬奇比例：</strong>
          {{ results[0].Da_Vinci || '数据缺失' }} (黄金比例)
          <p>描述：达芬奇比例接近黄金比例1.618是面部对称的理想值。</p>
        </li>
        <li>
          <strong>综合评分：</strong>
          {{ results[0].Overall_Score || '数据缺失' }} (颜值综合评分)
          <p>描述：该评分结合了五眼比例、三庭比例等指标来评估颜值的综合评分。</p>
        </li>
      </ul>
    </div>

    <div v-if="results">
      <h3>完整结果：</h3>
      <pre>{{ results }}</pre> <!-- 显示完整的 results 对象 -->
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

h2 {
  font-size: 24px;
  margin-bottom: 20px;
}

ul {
  list-style-type: none;
  padding: 0;
}

ul li {
  margin-bottom: 15px;
}

strong {
  color: #007bff;
}

p {
  font-size: 14px;
  color: #555;
  margin-top: 5px;
}
</style>
