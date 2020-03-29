import Vue from 'vue'
import VueRouter from 'vue-router'
import DocsMap from '../components/DocsMap.vue'
import HierarchicalTree from '../views/HierarchicalTree.vue'
import HierarchicalTree2 from '../views/HierarchicalTree2.vue'
import RadialLayout from '../views/RadialLayout.vue'

Vue.use(VueRouter)

const router = new VueRouter({
  // mode: 'history',
  routes: [
    { path:'/', component: DocsMap },
    { path: '/docsmap', name: 'DocsMap', component: DocsMap },
    { path: '/tree', name: 'HierarchicalTree', component: HierarchicalTree },
    { path: '/tree2', name: 'HierarchicalTree2', component: HierarchicalTree2 },
    { path: '/radial', name: 'RadialLayout', component: RadialLayout },
  ]
});

export default router;