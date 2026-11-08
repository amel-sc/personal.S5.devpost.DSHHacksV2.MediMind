import { createRouter, createWebHistory } from 'vue-router'
import ConversationView from '@/views/ConversationView.vue'
import HumeurListView from '@/views/HumeurListView.vue'
import HumeurDetailView from '@/views/HumeurDetailView.vue'
import HumeurFormView from '@/views/HumeurFormView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const routes = [
  { path: '/', redirect: { name: 'conversation' } },
  { path: '/conversation/:id([1-9]\\d*)?', name: 'conversation', component: ConversationView },
  {
    path: '/humeur/list',
    name: 'humeurList',
    component: HumeurListView,
    meta: { titre: "Journal d'humeur", section: 'humeur' },
  },
  {
    path: '/humeur/new',
    name: 'humeurCreate',
    component: HumeurFormView,
    meta: { titre: 'Nouvelle humeur', section: 'humeur' },
  },
  {
    path: '/humeur/:id([1-9]\\d*)',
    name: 'humeurDetail',
    component: HumeurDetailView,
    props: true,
    meta: { titre: "Détail de l'humeur", section: 'humeur' },
  },
  { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundView, meta: { titre: 'Page introuvable' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// La route conversation n'a pas de meta.titre : c'est la vue qui gère son titre
router.afterEach((to) => {
  if (to.meta.titre) document.title = `${to.meta.titre} · MediMind`
})

export default router
