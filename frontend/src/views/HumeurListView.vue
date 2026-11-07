<script setup>
import { computed, onMounted, ref } from 'vue'
import { api, ApiError } from '@/services/api'
import { dateHeure } from '@/utils/format'
import { niveauHumeur, estDifficile, estActive, versDate } from '@/utils/humeur'
import HumeurDetail from '@/components/HumeurDetail.vue'

const humeurToday = ref(null)
const humeurJours = ref([])
const chargement = ref(true)
const erreur = ref(null)
const periode = ref('30') // '7' | '30' | '90' | 'tout'

function messageErreur(e) {
  if (e instanceof ApiError) {
    return e.status >= 500
      ? 'Le serveur rencontre un problème. Réessayez dans un instant.'
      : e.message
  }
  return 'Impossible de joindre le serveur. Vérifiez votre connexion.'
}

async function charger() {
  chargement.value = true
  erreur.value = null

  // En parallèle : si "today" échoue, la liste s'affiche quand même
  const [liste, today] = await Promise.allSettled([
    api.humeurJours.lister(),
    api.humeurJours.today(),
  ])

  if (liste.status === 'fulfilled') {
    humeurJours.value = liste.value?.data ?? []
  } else {
    console.error(liste.reason)
    erreur.value = messageErreur(liste.reason)
  }

  if (today.status === 'fulfilled') {
    humeurToday.value = today.value // { humeur_jours, humeur_jours_causes }
  } else {
    console.error(today.reason)
    humeurToday.value = null
  }

  chargement.value = false
}

const aHumeurAujourdhui = computed(() => !!humeurToday.value?.humeur_jours)

// Le backend trie déjà par date_creation DESC
const humeursFiltrees = computed(() => {
  if (periode.value === 'tout') return humeurJours.value
  const limite = Date.now() - Number(periode.value) * 24 * 60 * 60 * 1000
  return humeurJours.value.filter((h) => (versDate(h.date_creation)?.getTime() ?? 0) >= limite)
})

const activesFiltrees = computed(() => humeursFiltrees.value.filter(estActive))

const formatMois = new Intl.DateTimeFormat('fr-FR', { month: 'long', year: 'numeric' })

const groupes = computed(() => {
  const map = new Map()
  for (const h of humeursFiltrees.value) {
    const d = versDate(h.date_creation)
    const cle = d ? `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}` : 'inconnue'
    if (!map.has(cle)) {
      map.set(cle, { cle, libelle: d ? formatMois.format(d) : 'Date inconnue', items: [] })
    }
    map.get(cle).items.push(h)
  }
  return [...map.values()]
})

const stats = computed(() => {
  const compte = new Map()
  for (const h of activesFiltrees.value) {
    if (h.humeur_val == null) continue
    const c = compte.get(h.humeur_val) ?? { val: h.humeur_val, desce: h.humeur_desce, n: 0 }
    c.n++
    compte.set(h.humeur_val, c)
  }
  return {
    total: activesFiltrees.value.length,
    difficiles: activesFiltrees.value.filter((h) => estDifficile(h.humeur_val)).length,
    plusFrequente: [...compte.values()].sort((a, b) => b.n - a.n)[0] ?? null,
  }
})

// Les 3 dernières humeurs actives sont "Mal" ou "Très mal" → on propose de l'aide
const humeursBassesRecentes = computed(() => {
  const dernieres = humeurJours.value.filter(estActive).slice(0, 3)
  return dernieres.length === 3 && dernieres.every((h) => estDifficile(h.humeur_val))
})

const annonce = computed(() =>
  chargement.value
    ? 'Chargement de vos humeurs…'
    : `${humeursFiltrees.value.length} humeur(s) affichée(s).`
)

onMounted(charger)
</script>

<template>
  <div class="flex-grow-1 overflow-auto">
    <div class="container py-4 page-humeur">
      <!-- En-tête -->
      <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
        <div>
          <h1 class="h3 mb-1">Mon journal d'humeur</h1>
          <p class="mb-0 opacity-75">Suivez votre ressenti, jour après jour.</p>
        </div>
        <RouterLink to="/humeur/new" class="theme-primary btn-solid btn-styled">
          <i class="bi bi-plus-lg" aria-hidden="true"></i>
          {{ aHumeurAujourdhui ? 'Nouvelle humeur' : 'Noter mon humeur du jour' }}
        </RouterLink>
      </div>

      <p class="visually-hidden" aria-live="polite">{{ annonce }}</p>

      <!-- Soutien -->
      <aside v-if="humeursBassesRecentes" class="alert theme-info mb-4" aria-label="Soutien">
        <p class="fw-semibold mb-1">Ces derniers jours semblent difficiles.</p>
        <p class="mb-2">Vous n'êtes pas seul·e. En parler peut vraiment aider.</p>
        <div class="d-flex flex-wrap gap-2">
          <RouterLink :to="{ name: 'conversation' }" class="btn-outline theme-primary btn-styled">
            <i class="bi bi-chat-heart" aria-hidden="true"></i> Parler avec MediMind
          </RouterLink>
          <a href="tel:3114" class="btn-outline theme-primary btn-styled">
            <i class="bi bi-telephone" aria-hidden="true"></i> 3114 (gratuit, 24h/24)
          </a>
        </div>
      </aside>

      <!-- Humeur du jour -->
      <section v-if="aHumeurAujourdhui" class="mb-4">
        <HumeurDetail
          :humeur-jours="humeurToday.humeur_jours"
          :humeur-jours-causes="humeurToday.humeur_jours_causes"
        />
      </section>

      <!-- Historique -->
      <section aria-labelledby="titre-historique" :aria-busy="chargement">
        <div class="d-flex flex-wrap align-items-end justify-content-between gap-3 mb-3">
          <h2 id="titre-historique" class="h5 mb-0">Historique</h2>
          <div>
            <label for="filtre-periode" class="form-label small mb-1">Période</label>
            <select id="filtre-periode" v-model="periode" class="form-select">
              <option value="7">7 derniers jours</option>
              <option value="30">30 derniers jours</option>
              <option value="90">3 derniers mois</option>
              <option value="tout">Tout</option>
            </select>
          </div>
        </div>

        <!-- Chargement -->
        <div v-if="chargement" class="d-flex justify-content-center py-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Chargement…</span>
          </div>
        </div>

        <!-- Erreur -->
        <div v-else-if="erreur" class="alert theme-danger" role="alert">
          <p class="mb-2">{{ erreur }}</p>
          <button type="button" class="btn-outline theme-danger btn-styled" @click="charger">
            Réessayer
          </button>
        </div>

        <!-- Vide -->
        <div v-else-if="humeursFiltrees.length === 0" class="text-center py-5">
          <p class="fs-1 mb-2" aria-hidden="true">🌱</p>
          <p class="mb-3">
            {{ humeurJours.length === 0
              ? "Vous n'avez encore noté aucune humeur."
              : 'Aucune humeur sur cette période.' }}
          </p>
          <button
            v-if="humeurJours.length > 0"
            type="button"
            class="btn-text theme-primary"
            @click="periode = 'tout'"
          >
            Afficher tout l'historique
          </button>
        </div>

        <!-- Liste -->
        <template v-else>
          <dl class="stats d-flex flex-wrap gap-3 mb-4">
            <div class="card card-body py-2">
              <dt class="small opacity-75">Entrées</dt>
              <dd class="fs-4 fw-semibold mb-0">{{ stats.total }}</dd>
            </div>
            <div v-if="stats.plusFrequente" class="card card-body py-2">
              <dt class="small opacity-75">Humeur la plus fréquente</dt>
              <dd class="fs-5 fw-semibold mb-0">
                <span aria-hidden="true">{{ niveauHumeur(stats.plusFrequente.val).emoji }}</span>
                {{ stats.plusFrequente.desce }}
              </dd>
            </div>
            <div class="card card-body py-2">
              <dt class="small opacity-75">Jours difficiles</dt>
              <dd class="fs-4 fw-semibold mb-0">{{ stats.difficiles }}</dd>
            </div>
          </dl>

          <section
            v-for="groupe in groupes"
            :key="groupe.cle"
            :aria-labelledby="`mois-${groupe.cle}`"
            class="mb-4"
          >
            <h3 :id="`mois-${groupe.cle}`" class="h6 titre-mois opacity-75 mb-2">
              {{ groupe.libelle }}
            </h3>
            <ul class="list-unstyled d-flex flex-column gap-2 mb-0">
              <li v-for="h in groupe.items" :key="h.id">
                <RouterLink
                  :to="`/humeur/${h.id}`"
                  class="card carte-humeur"
                  :class="{ inactive: !estActive(h) }"
                >
                  <div class="card-body d-flex align-items-center gap-3 py-2">
                    <span class="fs-3" aria-hidden="true">{{ niveauHumeur(h.humeur_val).emoji }}</span>
                    <div class="flex-grow-1 min-w-0">
                      <p class="fw-semibold mb-0 text-truncate">
                        {{ h.humeur_desce ?? 'Humeur non renseignée' }}
                      </p>
                      <p v-if="h.note" class="small mb-0 text-truncate">{{ h.note }}</p>
                      <time :datetime="h.date_creation" class="small opacity-75">
                        {{ dateHeure(h.date_creation) }}
                      </time>
                    </div>
                    <span
                      v-if="!estActive(h) && h.status_desce"
                      class="badge badge-outline theme-secondary"
                    >
                      {{ h.status_desce }}
                    </span>
                    <i class="bi bi-chevron-right opacity-50" aria-hidden="true"></i>
                  </div>
                </RouterLink>
              </li>
            </ul>
          </section>
        </template>
      </section>
    </div>
  </div>
</template>

<style scoped>
.page-humeur {
  max-width: 48rem;
}
.titre-mois {
  text-transform: capitalize;
}
.min-w-0 {
  min-width: 0;
}
.stats > div {
  min-width: 9rem;
  flex: 1 1 0;
}
.stats dd {
  margin-inline-start: 0;
}
.carte-humeur {
  color: inherit;
  text-decoration: none;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.carte-humeur.inactive {
  opacity: 0.7;
}
.carte-humeur:hover {
  transform: translateY(-1px);
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.08);
}
.carte-humeur:focus-visible {
  outline: 3px solid var(--theme-focus-ring, currentColor);
  outline-offset: 2px;
}
@media (prefers-reduced-motion: reduce) {
  .carte-humeur {
    transition: none;
  }
  .carte-humeur:hover {
    transform: none;
  }
}
</style>
