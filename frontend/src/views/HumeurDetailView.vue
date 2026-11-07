<script setup>
import { computed, ref, watch, watchEffect } from 'vue'
import { api, ApiError } from '@/services/api'
import { messageErreur } from '@/utils/erreur'
import { versDate, estActive, estDifficile } from '@/utils/humeur'
import HumeurDetail from '@/components/HumeurDetail.vue'

const props = defineProps({ id: { type: String, required: true } })

const humeurJours = ref(null)
const humeurJoursCauses = ref([])
const chargement = ref(true)
const erreur = ref(null)
const introuvable = ref(false)

// Si l'id change vite, on ignore les réponses des anciennes requêtes
let requeteCourante = 0

async function charger() {
  const numero = ++requeteCourante
  chargement.value = true
  erreur.value = null
  introuvable.value = false
  humeurJours.value = null
  humeurJoursCauses.value = []

  // "/humeur/abc" : inutile d'appeler l'API
  if (!/^[1-9]\d*$/.test(props.id)) {
    introuvable.value = true
    chargement.value = false
    return
  }

  try {
    const response = await api.humeurJours.find(props.id)
    if (numero !== requeteCourante) return

    if (!response?.humeur_jours) {
      introuvable.value = true // au cas où le backend renverrait encore 200 + null
      return
    }
    humeurJours.value = response.humeur_jours
    humeurJoursCauses.value = response.humeur_jours_causes ?? []
  } catch (e) {
    if (numero !== requeteCourante) return
    console.error(e)
    if (e instanceof ApiError && e.status === 404) introuvable.value = true
    else erreur.value = messageErreur(e)
  } finally {
    if (numero === requeteCourante) chargement.value = false
  }
}

// Remplace onMounted : se relance aussi quand on passe de /humeur/3 à /humeur/5
watch(() => props.id, charger, { immediate: true })

const formatJour = new Intl.DateTimeFormat('fr-FR', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
})
const formatHeure = new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit' })

const date = computed(() => versDate(humeurJours.value?.date_creation))
const titre = computed(() =>
  date.value ? `Humeur du ${formatJour.format(date.value)}` : "Détail de l'humeur"
)
const estAujourdhui = computed(
  () => !!date.value && date.value.toDateString() === new Date().toDateString()
)
const remplacee = computed(() => !!humeurJours.value && !estActive(humeurJours.value))
const difficile = computed(() => estDifficile(humeurJours.value?.humeur_val))

// Titre de l'onglet (utile aussi pour les lecteurs d'écran)
watchEffect(() => {
  if (chargement.value) return
  document.title = introuvable.value
    ? 'Humeur introuvable · MediMind'
    : `${titre.value} · MediMind`
})
</script>

<template>
  <div class="flex-grow-1 overflow-auto">
    <div class="container py-4 page-detail" :aria-busy="chargement">
      <RouterLink to="/humeur/list" class="btn-text theme-inverse lien-retour mb-3">
        <i class="bi bi-arrow-left" aria-hidden="true"></i>
        Retour au journal
      </RouterLink>

      <!-- Chargement -->
      <div v-if="chargement" class="centre py-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Chargement de l'humeur…</span>
        </div>
      </div>

      <!-- Introuvable -->
      <div v-else-if="introuvable" class="etat-vide py-5">
        <p class="fs-1 mb-2" aria-hidden="true">🔍</p>
        <h1 class="h4 mb-2">Humeur introuvable</h1>
        <p class="opacity-75 mb-4">Cette entrée n'existe pas ou a été supprimée.</p>
        <RouterLink to="/humeur/list" class="btn-solid theme-primary btn-styled">
          Voir mon journal
        </RouterLink>
      </div>

      <!-- Erreur -->
      <template v-else-if="erreur">
        <h1 class="h3 mb-3">Détail de l'humeur</h1>
        <div class="alert theme-danger" role="alert">
          <p class="mb-2">{{ erreur }}</p>
          <button type="button" class="btn-outline theme-danger btn-styled" @click="charger">
            Réessayer
          </button>
        </div>
      </template>

      <!-- Contenu -->
      <template v-else-if="humeurJours">
        <header class="mb-4">
          <h1 class="h3 mb-1 titre-page">{{ titre }}</h1>
          <p class="meta mb-0">
            <span v-if="date" class="opacity-75">
              Notée à
              <time :datetime="humeurJours.date_creation">{{ formatHeure.format(date) }}</time>
            </span>
            <span v-if="estAujourdhui" class="badge badge-subtle theme-primary">Aujourd'hui</span>
            <span v-if="remplacee" class="badge badge-outline theme-secondary">
              {{ humeurJours.status_desce ?? 'Remplacée' }}
            </span>
          </p>
        </header>

        <div v-if="remplacee" class="alert theme-secondary mb-4">
          <p class="mb-0">
            <i class="bi bi-info-circle" aria-hidden="true"></i>
            Cette saisie a été remplacée par une autre le même jour.
            Elle n'est pas prise en compte dans vos statistiques.
          </p>
        </div>

        <HumeurDetail
          class="mb-4"
          titre="Votre ressenti"
          :humeur-jours="humeurJours"
          :humeur-jours-causes="humeurJoursCauses"
        />

        <aside v-if="difficile" class="alert theme-info mb-4" aria-label="Soutien">
          <p class="mb-0">
            Si ce moment est encore difficile, vous n'êtes pas seul·e.
            En cas de détresse, le <a href="tel:3114">3114</a> répond gratuitement, 24h/24.
          </p>
        </aside>

        <div class="actions">
          <RouterLink
            v-if="estAujourdhui && !remplacee"
            to="/humeur/new"
            class="btn-outline theme-primary btn-styled"
          >
            <i class="bi bi-pencil" aria-hidden="true"></i>
            Mettre à jour mon humeur du jour
          </RouterLink>
          <RouterLink :to="{ name: 'conversation' }" class="btn-solid theme-primary btn-styled">
            <i class="bi bi-chat-heart" aria-hidden="true"></i>
            En parler avec MediMind
          </RouterLink>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.page-detail {
  max-width: 40rem;
}
.lien-retour {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
.centre {
  display: flex;
  justify-content: center;
}
.etat-vide {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.titre-page::first-letter {
  text-transform: uppercase;
}
.meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.75rem;
}
@media (max-width: 36rem) {
  .actions {
    flex-direction: column;
  }
  .actions > * {
    width: 100%;
    justify-content: center;
  }
}
.entete-app {
  background-color: var(--mm-surface);
}
</style>