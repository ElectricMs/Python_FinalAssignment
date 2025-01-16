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
          <strong>五眼比例：</strong>
          {{ results[0].Five_Eye_Metrics || '数据缺失' }} (五眼比例)
          <p>描述：，“五眼比例”表示两眼之间的距离是否对称以及是否符合理想比例。五眼比例偏差越小，脸部宽度分布越对称。</p>
        </li>
        <li>
          <strong>三庭比例：</strong>
          <ul>
            <li>中庭与上下庭比例的差异: {{ results[0].Three_Section_Metric_A || '数据缺失' }}%</li>
            <li>中庭高度与整体平均比例的偏差: {{ results[0].Three_Section_Metric_B || '数据缺失' }}%</li>
            <li>上下庭对称性的偏差: {{ results[0].Three_Section_Metric_C || '数据缺失' }}%</li>
          </ul>
          <p>描述：人脸垂直方向被划分为“上庭（额头）”、“中庭（鼻子）”、“下庭（嘴巴和下巴）”三部分，三庭比例衡量这些区域的高度是否符合理想。三个数据越小越好。</p>
        </li>
        <li>
          <strong>达芬奇比例：</strong>
          {{ results[0].Da_Vinci || '数据缺失' }} (黄金比例)
          <p>描述：达芬奇比例接近黄金比例1.618是面部对称的理想值。</p>
        </li>
        <li>
          <strong>内眼角开合度：</strong>
          <ul>
            <li>左眼内角开合度: {{ results[0].EB_Metric_G || '数据缺失' }}%</li>
            <li>右眼内角开合度: {{ results[0].EB_Metric_H || '数据缺失' }}%</li>
          </ul>
          <p>描述：角度越接近理想值（50°），眼部开合越自然美观。</p>
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
