// Le routeur associe une URL à une vue (un composant « page »).
import { createRouter, createWebHistory } from 'vue-router'
import AccueilView from '../views/AccueilView.vue'
import FormationDetailView from '../views/FormationDetailView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import Apropos from '../views/Apropos.vue'

const routes = [
    { path: '/', redirect: { name: 'conversation' } },
    // :id? = optionnel, donc /conversation = nouvelle conversation
    { path: '/conversation/:id?', name: 'conversation', component: ConversationView },
    { path: '/parametres', name: 'parametres', component: ParametresView }
]

export default createRouter({
  // Mode « history » : de vraies URL (/formations/3), sans # dans l'adresse
  history: createWebHistory(),
  routes
})
