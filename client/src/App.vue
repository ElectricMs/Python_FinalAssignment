<template>
  <div id="app">
    <h1>实时人脸识别打分</h1>
    <Webcam />
  </div>
</template>

<script>
import Webcam from "./components/WebcamComponent.vue";

export default {
  name: "App",
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
  color: #333;
}
</style>
