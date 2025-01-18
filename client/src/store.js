import { createStore } from 'vuex';

export default createStore({
  state: {
    imageSrc: null, // 存储图片的base64字符串或URL
    jsonData: {}    // 存储你的JSON数据
  },
  mutations: {
    setImageSrc(state, payload) {
      state.imageSrc = payload;
    },
    setJsonData(state, payload) {
      state.jsonData = payload;
    }
  },
  actions: {
    updateImageSrc({ commit }, payload) {
      commit('setImageSrc', payload);
    },
    updateJsonData({ commit }, payload) {
      commit('setJsonData', payload);
    }
  },
  getters: {
    getImageSrc: state => state.imageSrc,
    getJsonData: state => state.jsonData
  }
});