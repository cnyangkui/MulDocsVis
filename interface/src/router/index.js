import Vue from 'vue'
import VueRouter from 'vue-router'
import DocsMap from '../components/DocsMap.vue'

Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  routes: [
    { path:'/', component: DocsMap },
    { path: '/docsmap', name: 'docsmap', component: DocsMap }
  ]
});

export default router;