import { createRouter, createWebHistory } from 'vue-router'
import ConversationView from '@/views/ConversationView.vue'
import HumeurListView from '@/views/HumeurListView.vue'
import HumeurDetailView from '@/views/HumeurDetailView.vue'
import HumeurFormView from '@/views/HumeurFormView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import InscriptionView from '@/views/InscriptionView.vue'
import ConnexionView from '@/views/ConnexionView.vue'
import { i18n } from '@/i18n'
import { watch } from 'vue'
import { api } from '@/services/api'

const routes = [
  { 
    path: '/', 
    redirect: { name: 'conversation' } 
  },
  { 
    path: '/conversation/:id([1-9]\\d*)?', 
    name: 'conversation', 
    component: ConversationView, 
    meta: { requiresAuth: true }, 
  },
  {
    path: '/inscription',
    name: 'inscription',
    component: InscriptionView,
    meta: { titre: "Inscription" },
  },
  {
    path: '/connexion',
    name: 'connexion',
    component: ConnexionView,
    meta: { titre: "Connexion" },
  },
  {
    path: '/humeur/list',
    name: 'humeurList',
    component: HumeurListView,
    meta: { titre: "Journal d'humeur", section: 'humeur', requiresAuth: true },
  },
  {
    path: '/humeur/new',
    name: 'humeurCreate',
    component: HumeurFormView,
    meta: { titre: 'Nouvelle humeur', section: 'humeur', requiresAuth: true },
  },
  {
    path: '/humeur/:id([1-9]\\d*)',
    name: 'humeurDetail',
    component: HumeurDetailView,
    props: true,
    meta: { section: 'humeur', requiresAuth: true },
  },
  { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundView, meta: { titre: 'Page introuvable' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

function mettreTitre(route) {
  if (route.meta.titre) document.title = `${i18n.global.t(route.meta.titre)} · MediMind`
}

router.beforeEach(async (to) => {
  if (!to.matched.some((route) => route.meta.requiresAuth)) {
    return true
  }

  try {
    await api.auth.moi()
    return true
  } catch (e) {
    if (e.status === 401) {
      return {
        name: 'connexion',
        query: { redirect: to.fullPath },
      }
    }

    // Une erreur réseau ou serveur n'est pas une preuve de déconnexion.
    // Affiche plutôt un écran d'erreur ou laisse la navigation continuer
    // selon le comportement souhaité.
    return true
  }
})

// La route conversation n'a pas de meta.titre : c'est la vue qui gère son titre
router.afterEach(mettreTitre)

// Le titre change aussi quand on change de langue, sans naviguer
watch(i18n.global.locale, () => mettreTitre(router.currentRoute.value))

export default router
