// Le routeur associe une URL à une vue (un composant « page »).
import { createRouter, createWebHistory } from 'vue-router'
import ConversationView from '@/views/ConversationView.vue'
import HumeurListView from '@/views/HumeurListView.vue'

const routes = [
    { path: '/', redirect: { name: 'conversation' } },
    // :id? = optionnel, donc /conversation = nouvelle conversation
    { path: '/conversation/:id?', name: 'conversation', component: ConversationView },
    { path: '/humeur/list', name: 'humeurList', component: HumeurListView }
]

export default createRouter({
  // Mode « history » : de vraies URL (/formations/3), sans # dans l'adresse
  history: createWebHistory(),
  routes
})
