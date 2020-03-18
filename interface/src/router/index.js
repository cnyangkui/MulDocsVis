import Vue from 'vue'
import VueRouter from 'vue-router'
import DocsMap from '../components/DocsMap.vue'
import HierarchicalTree from '../views/HierarchicalTree.vue'
import HierarchicalTree2 from '../views/HierarchicalTree2.vue'

Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  routes: [
    { path:'/', component: DocsMap },
    { path: '/docsmap', name: 'docsMap', component: DocsMap },
    { path: '/tree', name: 'hierarchicalTree', component: HierarchicalTree },
    { path: '/tree2', name: 'hierarchicalTree2', component: HierarchicalTree2 }
  ]
});

export default router;