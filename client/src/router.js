// router.js
import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/components/HomePage.vue';
import ResultPage from '@/components/ResultPage.vue';
import WebcamComponent from '@/components/WebcamComponent.vue';
const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: HomePage,
    
  },
  {
    path: '/result',
    name: 'ResultPage',
    component: ResultPage,
  },
  {
    path:'/Webcam',
    name:'WebcamComponent',
    component: WebcamComponent,
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
