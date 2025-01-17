<template>
  <div class="webcam-container">
    <div v-if="imageSrc" class="image-container">
      <h2>实时画面</h2>
      <img :src="imageSrc" alt="Webcam Stream" class="webcam-image" />
    </div>

    <div v-if="results && results.length > 0" class="results-container">
      <h2>实时分析结果</h2>
      <ul class="results-list">
        <li>
          <strong>五眼比例：</strong>
          {{ results[0].five_eye_metrics || '数据缺失' }} (五眼比例)
          <p>描述：五眼比例表示两眼之间的距离对称性以及是否符合理想比例。偏差越小，脸部宽度分布越对称。</p>
        </li>

        <li>
          <strong>三庭比例：</strong>
          <ul v-if="results[0].three_section_metrics" class="sub-results-list">
            <li>中庭与上下庭比例的差异: {{ results[0].three_section_metrics.metric_a || '数据缺失' }}</li>
            <li>中庭高度与整体平均比例的偏差: {{ results[0].three_section_metrics.metric_b || '数据缺失' }}</li>
            <li>上下庭对称性的偏差: {{ results[0].three_section_metrics.metric_c || '数据缺失' }}</li>
          </ul>
          <p>描述：人脸垂直方向被划分为"上庭（额头）"、"中庭（鼻子）"、"下庭（嘴巴和下巴）"三部分，衡量这些区域的高度比例。数值越小越好。</p>
        </li>
        <li>
          <strong>达芬奇比例：</strong>
          {{ results[0].da_vinci_ratio || '数据缺失' }} (黄金比例)
          <p>黄金比例接近1.618是理想的面部对称值。</p>
        </li>
        <li>
          <strong>内眼角开合度：</strong>
          <ul v-if="results[0].eye_angle_metrics" class="sub-results-list">
            <li>左眼内角开合度: {{ results[0].eye_angle_metrics.left_eye || '数据缺失' }}°</li>
            <li>右眼内角开合度: {{ results[0].eye_angle_metrics.right_eye || '数据缺失' }}°</li>
          </ul>
          <p>描述：角度越接近理想值（50°），眼部开合越自然美观。</p>
        </li>
        <!-- 对称性评分 -->
        <li v-if="results[0].symmetry_metrics">
          <strong>面部对称性：</strong>
          <ul>
            <li>整体对称性: {{ (results[0].symmetry_metrics.overall_symmetry * 100).toFixed(2) || '数据缺失' }}%</li>
            <li v-for="(value, key) in results[0].symmetry_metrics.feature_symmetry" :key="key">
              {{ key }}: {{ (value * 100).toFixed(2) }}%
            </li>
          </ul>
          <p>描述：评估面部左右对称程度，分数越高表示对称性越好。</p>
        </li>
        <!-- 黄金分割比例 -->
        <li v-if="results[0].golden_ratio_metrics">
          <strong>黄金分割比例：</strong>
          <ul>
            <li>整体比例: {{ (results[0].golden_ratio_metrics.overall_ratio * 100).toFixed(2) || '数据缺失' }}%</li>
            <li v-for="(value, key) in results[0].golden_ratio_metrics.feature_ratios" :key="key">
              {{ formatRatioName(key) }}: {{ (value * 100).toFixed(2) }}%
            </li>
          </ul>
          <p>描述：评估面部各部分是否符合黄金分割比例，分数越高表示越接近理想比例。</p>
        </li>
        <!-- 脸型分析 -->
        <li v-if="results[0].face_shape_metrics">
          <strong>脸型分析：</strong>
          <ul>
            <li v-for="(score, shape) in results[0].face_shape_metrics" :key="shape">
              {{ formatFaceShape(shape) }}: {{ (score * 100).toFixed(2) }}%
            </li>
          </ul>
          <p>描述：分析面部轮廓与各种典型脸型的匹配程度。</p>
        </li>

        <!-- 综合评分 -->
        <li v-if="results[0].overall_score !== undefined">
          <strong>综合评分：</strong>
          {{ results[0].overall_score?.toFixed(2) || '数据缺失' }} (颜值综合评分)
          <p>描述：结合所有面部特征指标的综合评估分数。</p>
        </li>
      </ul>
    </div>

    <div v-if="results" class="full-results-container">
      <h3>完整结果：</h3>
      <pre class="results-pre">{{ results }}</pre>
    </div>

    <button v-if="buttonshow" @click="startWebSocket" class="start-button">开始实时打分</button>
    <button v-if="imageSrc" @click="changePage" class="start-button">结束打分</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      buttonshow: true,
      websocket: null,
      imageSrc: null,
      results: null,
      isConnected: false,
      clientId: null
    };
  },
  methods: {
    startWebSocket() {
      if(this.buttonshow==true){
        this.buttonshow = false;
      }

            // 生成唯一的客户端ID
            this.clientId = 'client_' + Date.now();
      
      // 使用新的WebSocket地址格式
      this.websocket = new WebSocket(`ws://127.0.0.1:8000/api/v1/ws/${this.clientId}`);
      
      this.websocket.onopen = () => {
        console.log('WebSocket连接已建立');
        this.isConnected = true;
      };

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('收到WebSocket消息:', data); // 调试日志

        if (data.type === 'frame_processed') {
          const processData = data.data;
          
          if (processData.status === 'success') {
            if (processData.image) {
              this.imageSrc = `data:image/jpeg;base64,${processData.image}`;
            }
            if (processData.metrics) {
              console.log('收到的metrics数据:', processData.metrics); // 调试日志
              this.results = processData.metrics;
            }
          } else if (processData.status === 'error') {
            console.error('处理错误:', processData.error);
          }
        }
      };

      this.websocket.onerror = (error) => {
        console.error("WebSocket错误:", error);
        this.isConnected = false;
        alert("连接失败，请检查后端服务是否启动！");
      };

      this.websocket.onclose = () => {
        console.log("WebSocket连接已关闭");
        this.isConnected = false;
        this.websocket = null;
      };
    },

    formatFaceShape(shape) {
      const shapeNames = {
        'oval': '椭圆形',
        'round': '圆形',
        'square': '方形',
        'heart': '心形',
        'diamond': '钻石形'
      };
      return shapeNames[shape] || shape;
    },

    formatRatioName(key) {
      const ratioNames = {
        'forehead_nose_ratio': '额头-鼻子比例',
        'nose_chin_ratio': '鼻子-下巴比例',
        'eye_spacing_ratio': '眼睛间距比例',
        'lip_nose_ratio': '嘴唇-鼻子比例'
      };
      return ratioNames[key] || key;
    },
    changePage() {

      // 准备要更新的数据
      const newImageSrc = this.imageSrc;
      const newJsonData =this.results;

        // 分别调用两个actions来更新Vuex状态
      this.$store.dispatch('updateImageSrc', newImageSrc);
      this.$store.dispatch('updateJsonData', newJsonData);
      this.$router.push('/result');

    }
  },
};
</script>

<style>
.webcam-container {
  font-family: 'Roboto', sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.image-container {
  text-align: center;
  margin-bottom: 20px;
}

.webcam-image {
  max-width: 100%;
  border: 4px solid #ddd;
  border-radius: 12px;
  transition: transform 0.3s ease;
}

.webcam-image:hover {
  transform: scale(1.05);
}

h2, h3 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #333;
}

ul {
  list-style-type: none;
  padding: 0;
}

.results-list li {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f8f9fa;
  border-left: 4px solid #007bff;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.results-list li:hover {
  background-color: #eef5ff;
}

.sub-results-list {
  margin-left: 20px;
}

strong {
  color: #007bff;
}

p {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.start-button {
  display: block;
  margin: 20px auto 0;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: bold;
  background-color: #007bff;
  color: #fff;
  border: none;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.3s, transform 0.2s;
}

.start-button:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
}

.results-pre {
  background-color: #f4f4f4;
  padding: 10px;
  border-radius: 8px;
  overflow-x: auto;
}
</style>
