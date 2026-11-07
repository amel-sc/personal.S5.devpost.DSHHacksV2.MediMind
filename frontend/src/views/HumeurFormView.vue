<script setup>
import { onMounted, ref } from 'vue'
import HumeurForm from '@/components/HumeurForm.vue'
import { api } from '@/services/api'
import { messageErreur } from '@/utils/erreur'

const humeurs = ref([])
const humeurCauses = ref([])
const humeurToday = ref(null)
const chargement = ref(true)
const erreur = ref(null)

const dateDuJour = new Intl.DateTimeFormat('fr-FR', {
  weekday: 'long', day: 'numeric', month: 'long',
}).format(new Date())

async function charger() {
  chargement.value = true
  erreur.value = null

  const [rHumeurs, rCauses, rToday] = await Promise.allSettled([
    api.humeur.lister(),
    api.humeurCause.lister(),
    api.humeurJours.today(),
  ])

  if (rHumeurs.status === 'rejected' || rCauses.status === 'rejected') {
    const raison = rHumeurs.reason ?? rCauses.reason
    console.error(raison)
    erreur.value = messageErreur(raison)
  } else {
    humeurs.value = rHumeurs.value?.data ?? []
    humeurCauses.value = rCauses.value?.data ?? []
  }

  // Facultatif : sert seulement à prévenir qu'une humeur existe déjà
  humeurToday.value = rToday.status === 'fulfilled' ? rToday.value?.humeur_jours ?? null : null

  chargement.value = false
}

onMounted(charger)
</script>

<template>
  <div class="flex-grow-1 overflow-auto">
    <div class="container py-4 page-formulaire">
      <RouterLink to="/humeur/list" class="btn-text theme-inverse lien-retour mb-3">
        <i class="bi bi-arrow-left" aria-hidden="true"></i>
        Retour au journal
      </RouterLink>

      <h1 class="h3 mb-1">Comment ça va aujourd'hui ?</h1>
      <p class="opacity-75 mb-4 date-jour">{{ dateDuJour }}</p>

      <!-- Chargement -->
      <div v-if="chargement" class="d-flex justify-content-center py-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Chargement du formulaire…</span>
        </div>
      </div>

      <!-- Erreur -->
      <div v-else-if="erreur" class="alert theme-danger" role="alert">
        <p class="mb-2">{{ erreur }}</p>
        <button type="button" class="btn-outline theme-danger btn-styled" @click="charger">
          Réessayer
        </button>
      </div>

      <template v-else>
        <div v-if="humeurToday" class="alert theme-info mb-4">
          <p class="mb-0">
            <i class="bi bi-info-circle" aria-hidden="true"></i>
            Vous avez déjà noté votre humeur aujourd'hui
            (<strong>{{ humeurToday.humeur_desce }}</strong>).
            Cette nouvelle saisie la remplacera.
          </p>
        </div>

        <div class="card">
          <div class="card-body">
            <HumeurForm :humeurs="humeurs" :humeur-causes="humeurCauses" />
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.page-formulaire {
  max-width: 40rem;
}
.lien-retour {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
.date-jour::first-letter {
  text-transform: uppercase; /* « Samedi 7 novembre » */
}
</style>
