<template>
    <div>
      <h1>实时人脸识别打分系统</h1>
      <Webcam />
    </div>
</template>
  
<script>
  import Webcam from "./WebcamComponent.vue";
  
  export default {
    name: "HomePage",
    components: {
      Webcam,
    },
  };
</script>
  
<style>
  body {
    font-family: Arial, sans-serif;
    text-align: center;
    margin: 0;
    padding: 0;
    background-color: #f0f0f0;
  }
  
  h1 {
    margin-top: 20px;
    font-size: 25px;
    color: #333;
  }
</style>