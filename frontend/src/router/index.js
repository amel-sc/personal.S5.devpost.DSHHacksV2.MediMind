// Le routeur associe une URL à une vue (un composant « page »).
import { createRouter, createWebHistory } from 'vue-router'
import ConversationView from '@/views/ConversationView.vue'
import HumeurListView from '@/views/HumeurListView.vue'
import HumeurDetailView from '@/views/HumeurDetailView.vue'
import HumeurFormView from '@/views/HumeurFormView.vue'

const routes = [
  { path: '/', redirect: { name: 'conversation' } },
  {
    path: '/conversation/:id([1-9]\\d*)?',
    name: 'conversation',
    component: ConversationView,
    meta: { titre: 'Conversation' },
  },
  { path: '/humeur/list', name: 'humeurList', component: HumeurListView, meta: { titre: "Journal d'humeur" } },
  { path: '/humeur/new', name: 'humeurCreate', component: HumeurFormView, meta: { titre: 'Nouvelle humeur' } },
  {
    path: '/humeur/:id([1-9]\\d*)',
    name: 'humeurDetail',
    component: HumeurDetailView,
    props: true,
    meta: { titre: "Détail de l'humeur" },
  },
  { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundView, meta: { titre: 'Page introuvable' } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.afterEach((to) => {
  document.title = to.meta.titre ? `${to.meta.titre} · MediMind` : 'MediMind'
})
