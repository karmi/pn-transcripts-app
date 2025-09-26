import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import ListView from './views/ListView.vue'
import ItemView from './views/ItemView.vue'
import './style.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: ListView },
    { path: '/play/:id', component: ItemView, props: true }
  ]
})

createApp(App).use(router).mount('#app')
