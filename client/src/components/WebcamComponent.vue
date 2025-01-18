<template>
  <div class="webcam-container">
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>正在开启摄像头...</p>
    </div>

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
            <li>中庭与上下庭比例的差异: {{ results[0].three_section_metrics.Three_Section_Metric_A || '数据缺失' }}</li>
            <li>中庭高度与整体平均比例的偏差: {{ results[0].three_section_metrics.Three_Section_Metric_B || '数据缺失' }}</li>
            <li>上下庭对称性的偏差: {{ results[0].three_section_metrics.Three_Section_Metric_C || '数据缺失' }}</li>
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
            <li>左眼内角开合度: {{ results[0].eye_angle_metrics.EB_Metric_G || '数据缺失' }}°</li>
            <li>右眼内角开合度: {{ results[0].eye_angle_metrics.EB_Metric_H || '数据缺失' }}°</li>
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
            <li v-for="(value, key) in results[0].golden_ratio_metrics" :key="key" >
              {{ formatRatioName(key) }}: {{ (value * 100).toFixed(2) }}%
            </li>
          </ul>
          <p>描述：评估面部各部分是否符合黄金分割比例，越接近0.618表示越接近理想比例。</p>
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

    <img v-if="buttonshow" src="@/assets/banner.png" alt="" class="small-image">
    <div v-if="buttonshow" class="description">
        本项目基于Mediapipe和OpenCV库，检测脸部多个特征点的位置信息，通过美学计算公式，返回五眼比例、三庭比例、达芬奇比例、内眼角开合度、面部对称性、黄金分割比例等多个美学指数。
    </div>
    <div v-if="buttonshow" class="description2">
      综合以上的指数，打出客观的颜值评分，并给出用户的脸型分析。
    </div>

    <button v-if="buttonshow" @click="startWebSocket" class="start-button">开始实时打分</button>
    <button v-if="imageSrc" @click="changePage" class="start-button">结束打分并查看结果</button>
    <button v-if="buttonshow" @click="showAlgorithmModal" class="start-button">算法设计详情</button>

    <!-- 算法设计模态框 -->
    <div v-if="isAlgorithmModalVisible" class="algorithm-modal-overlay">
      <div class="algorithm-modal">
        <h2>算法设计</h2>
        <p>以下是我们的算法设计详情：</p>
        <p>1. 使用Mediapipe检测脸部特征点。</p>
        <p>2. 通过OpenCV进行图像处理。</p>
        <p>3. 计算五眼比例、三庭比例、达芬奇比例等美学指数。</p>
        <p>4. 评估面部对称性和黄金分割比例。</p>
        <p>5. 分析脸型并给出综合评分。</p>
        <button @click="hideAlgorithmModal" class="close-button">关闭</button>
      </div>
    </div>
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
      clientId: null,
      isLoading: false,
      isAlgorithmModalVisible: false, // 添加模态框显示状态
    };
  },
  methods: {
    formatRatioName(key) {
      const ratioNames = {
        'forehead_nose_ratio': '额头-鼻子比例',
        'nose_chin_ratio': '鼻子-下巴比例',
        'width_height_ratio': '宽度-高度的比例',
        'eye_spacing_ratio': '眼睛间距比例',
        'lip_nose_ratio': '嘴唇-鼻子比例',
        'overall_golden_ratio': '黄金分割比例'
      };
      return ratioNames[key] || key;
    },
    startWebSocket() {
      if (this.buttonshow) {
        this.buttonshow = false;
      }

      this.isLoading = true;

      this.clientId = 'client_' + Date.now();
      this.websocket = new WebSocket(`ws://127.0.0.1:8000/api/v1/ws/${this.clientId}`);

      this.websocket.onopen = () => {
        console.log('WebSocket连接已建立');
        this.isConnected = true;
        this.isLoading = false;
      };

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('收到WebSocket消息:', data);

        if (data.type === 'frame_processed') {
          const processData = data.data;

          if (processData.status === 'success') {
            if (processData.image) {
              this.imageSrc = `data:image/jpeg;base64,${processData.image}`;
            }
            if (processData.metrics) {
              console.log('收到的metrics数据:', processData.metrics);
              this.results = processData.metrics;
            }
          } else if (processData.status === 'error') {
            console.error('处理错误:', processData.error);
            this.isLoading = false;
          }
        }
      };

      this.websocket.onerror = (error) => {
        console.error("WebSocket错误:", error);
        this.isConnected = false;
        alert("连接失败，请检查后端服务是否启动！");
        this.isLoading = false;
      };

      this.websocket.onclose = () => {
        console.log("WebSocket连接已关闭");
        this.isConnected = false;
        this.websocket = null;
        this.isLoading = false;
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

    changePage() {
      const newImageSrc = this.imageSrc;
      const newJsonData = this.results;

      this.$store.dispatch('updateImageSrc', newImageSrc);
      this.$store.dispatch('updateJsonData', newJsonData);
      this.$router.push('/result');
    },

    showAlgorithmModal() {
      this.isAlgorithmModalVisible = true;
    },

    hideAlgorithmModal() {
      this.isAlgorithmModalVisible = false;
    }
  }
};
</script>

<style>
/* 其他样式 */

.small-image {
  width: 700px;
  height: auto;
  border-radius: 10px;
}

.description {
  color: gray;
  line-height: 30px;
  font-size: 20px;
  padding-left: 70px;
  padding-right: 70px;
  padding-top: 30px;
}

.description2 {
  font-weight: bold;
  line-height: 30px;
  font-size: 20px;
  padding-left: 40px;
  padding-right: 40px;
  padding-top: 30px;
  margin-bottom: 30px;
}

.webcam-container {
  font-family: 'Roboto', sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
}

@media (max-width: 768px) {
  .webcam-container {
    max-width: 100%;
    padding: 10px;
  }

  .small-image {
    width: 100%;
  }

  .description, .description2 {
    padding-left: 10px;
    padding-right: 10px;
  }

  .start-button {
    width: 100%;
    margin: 10px 0;
  }
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

/* 加载动画样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.689);
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  z-index: 1000;
}

.loading-spinner {
  border: 16px solid #f3f3f3;
  border-top: 16px solid #3498db;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 算法设计模态框样式 */
.algorithm-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
}

.algorithm-modal {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  width: 80%;
  max-width: 600px;
  text-align: center;
}

.algorithm-modal h2 {
  margin-bottom: 20px;
  color: #333;
}

.algorithm-modal p {
  font-size: 16px;
  color: #666;
  margin-bottom: 15px;
}

.close-button {  
  margin-top: 20px;
  padding: 10px 20px;
  font-size: 16px;
  font-weight: bold; 
  background-color: #0091ff;
  color: #333;
  border: none;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.3s, transform 0.2s;
}

.close-button:hover {
  background-color: #e6b800;
  transform: translateY(-2px);
}
</style>