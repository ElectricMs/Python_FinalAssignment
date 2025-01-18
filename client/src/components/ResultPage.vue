<template>
  <div>
    <!-- 包含图片的圆角白色容器 -->
    <div class="image-container">
      <div class="text1">
        <p>您的颜值分数是{{ faceAnalysisResults }}</p>
        <h2>获得称号：{{ awardTitle }}</h2>
        <p>{{ awardDescription }}</p>
      </div>
      <img :src="imageSrc" alt="Stored Image" class="stored-image">
      <button @click="changePage" class="start-button">回到主页面</button>
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    // 使用getter来获取store中的imageSrc
    imageSrc() {
      return this.$store.getters.getImageSrc;
    },
    faceAnalysisResults() {
      const results = this.$store.getters.getJsonData;
      // 获取Overall_Score并保留一位小数
      const overallScore = parseFloat(results[0].overall_score.toFixed(1));
      return overallScore;
    },
    awardTitle() {
      if (this.faceAnalysisResults < 60) return '潜力无限';
      if (this.faceAnalysisResults >= 60 && this.faceAnalysisResults < 70) return '邻家暖心';
      if (this.faceAnalysisResults >= 70 && this.faceAnalysisResults < 80) return '自然魅力';
      if (this.faceAnalysisResults >= 80 && this.faceAnalysisResults < 90) return '明星潜质';
      if (this.faceAnalysisResults >= 90 && this.faceAnalysisResults <= 100) return '颜值巅峰';
      return '无'; // 其他情况
    },
    awardDescription() {
      if (this.faceAnalysisResults === null) return '';
      if (this.faceAnalysisResults < 60) return "嘿，您的颜值就像是未完成的拼图，每一块都藏着无限可能！说不定下个转角，您就能解锁‘隐藏颜值技能’，让世界大吃一惊呢！记得，自信的笑容永远是最美的装饰哦！";
      if (this.faceAnalysisResults >= 60 && this.faceAnalysisResults < 70) return "您知道吗？在颜值界，您就像是那杯温暖的拿铁，不张扬却让人倍感舒心。走在街上，说不定能收获不少‘看着就好亲切’的微笑呢！记住，亲和力可是比颜值更难得的魅力哦！";
      if (this.faceAnalysisResults >= 70 && this.faceAnalysisResults < 80) return "您就像是春天里不经意间绽放的小花，不惊艳却自有一番风味。在这个滤镜横行的时代，您那份不加修饰的自然美，简直是清新脱俗的存在！让人忍不住多看几眼，感受那份真实的美好。";
      if (this.faceAnalysisResults >= 80 && this.faceAnalysisResults < 90) return "哎呀，您这颜值，简直就是从漫画里走出来的一样！走在街上，回头率那是杠杠的，说不定哪天就被星探发掘，成为下一个国民偶像呢！不过别忘了，内在的光芒和才华，才是让您更加闪耀的关键哦！";
      if (this.faceAnalysisResults >= 90 && this.faceAnalysisResults <= 100) return "恭喜您，成功解锁了‘人间绝色’成就！您的颜值，简直就是行走的美学教科书，让人不禁感叹：‘此颜只应天上有，人间难得几回闻’。不过，记得哦，最美的风景不只是外表，还有您那颗善良、独特的心。";
      return '无'; // 其他情况
    }
  },
  methods: {
    changePage() {
      // 首先进行路由跳转
      this.$router.push('/').then(() => {
        // 路由跳转完成后刷新页面
        window.location.reload();
      }).catch(err => {
        console.error('路由跳转失败:', err);
      });
    }
  }
}
</script>

<style scoped>
/* 样式可根据需要调整 */
.image-container {
  background-color: white; /* 设置背景颜色为白色 */
  border-radius: 15px; /* 设置圆角半径 */
  padding: 10px; /* 可选：给容器内部元素一些填充 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 可选：添加阴影效果 */
  width: 90%;
  max-width: 900px;
  margin: 0 auto;
  margin-top: 30px;
  padding: 30px;
  text-align: center;
}

.stored-image {
  max-width: 100%; /* 图片最大宽度为容器宽度 */
  height: auto; /* 保持图片比例 */
  display: block; /* 确保图片作为块级元素显示 */
  margin: 0 auto; /* 居中显示图片（如果需要） */
  border-radius: 10px; /* 如果希望图片也有圆角，可以设置此属性 */
}

.text1 {
  margin-bottom: 20px;
}

p {
  font-size: 16px;
  line-height: 1.6;
  margin: 10px 0;
}

h2 {
  font-size: 24px;
  margin: 10px 0;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .image-container {
    width: 95%;
    padding: 20px;
  }

  h2 {
    font-size: 20px;
  }

  p {
    font-size: 14px;
  }

  .start-button {
    width: 100%;
    margin: 15px 0;
  }
}

@media (max-width: 480px) {
  .image-container {
    width: 98%;
    padding: 15px;
  }

  h2 {
    font-size: 18px;
  }

  p {
    font-size: 12px;
  }

  .start-button { 
    width: 100%;
    margin: 10px 0;
  }
}
</style>