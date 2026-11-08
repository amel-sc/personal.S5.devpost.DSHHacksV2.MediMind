<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import HumeurForm from '@/components/HumeurForm.vue'
import { api } from '@/services/api'
import { messageErreur } from '@/utils/erreur'
import { libelleHumeur } from '@/utils/humeur'

const { t, locale } = useI18n()

const humeurs = ref([])
const humeurCauses = ref([])
const humeurToday = ref(null)
const causesToday = ref([])
const chargement = ref(true)
const erreur = ref(null) // objet erreur brut : traduit à l'affichage

const texteErreur = computed(() => (erreur.value ? messageErreur(erreur.value) : ''))

/* ---------- Date du jour ---------- */
const aujourdhui = new Date()
const dateIso = [
  aujourdhui.getFullYear(),
  String(aujourdhui.getMonth() + 1).padStart(2, '0'),
  String(aujourdhui.getDate()).padStart(2, '0'),
].join('-')
const dateDuJour = computed(() =>
  aujourdhui.toLocaleDateString(locale.value, { weekday: 'long', day: 'numeric', month: 'long' }),
)

/* ---------- Valeurs de départ si une humeur existe déjà aujourd'hui ---------- */
const initiale = computed(() => {
  if (!humeurToday.value) return null
  return {
    humeur: humeurToday.value.humeur_val,
    note: humeurToday.value.note ?? '',
    // id de la CAUSE (table humeur_cause), pas celui de la ligne de liaison
    causes: causesToday.value.map((c) => c.id_cause ?? c.id),
  }
})

async function charger() {
  chargement.value = true
  erreur.value = null

  const [rHumeurs, rCauses, rToday] = await Promise.allSettled([
    api.humeur.lister(),
    api.humeurCause.lister(),
    api.humeurJours.today(),
  ])

  if (rHumeurs.status === 'rejected' || rCauses.status === 'rejected') {
    const raison = rHumeurs.status === 'rejected' ? rHumeurs.reason : rCauses.reason
    console.error(raison)
    erreur.value = raison
  } else {
    humeurs.value = rHumeurs.value?.data ?? []
    humeurCauses.value = rCauses.value?.data ?? []
  }

  // Facultatif : une 404 ou une erreur ici ne bloque pas le formulaire
  const today = rToday.status === 'fulfilled' ? rToday.value : null
  humeurToday.value = today?.humeur_jours ?? null
  causesToday.value = today?.humeur_jours_causes ?? []

  chargement.value = false
}

onMounted(charger)
</script>

<template>
  <div class="vue-humeur-form">
    <div class="page-formulaire">
      <RouterLink to="/humeur/list" class="btn-text theme-inverse lien-retour">
        <i class="bi bi-arrow-left" aria-hidden="true"></i>
        {{ t('humeur.form.retour') }}
      </RouterLink>

      <header class="entete-page">
        <h1 class="titre-page">{{ t('humeur.form.titre') }}</h1>
        <p class="date-jour"><time :datetime="dateIso">{{ dateDuJour }}</time></p>
      </header>

      <!-- Chargement -->
      <div v-if="chargement" class="etat-chargement" role="status">
        <span class="mm-spinner" aria-hidden="true"></span>
        <span>{{ t('humeur.form.chargement') }}</span>
      </div>

      <!-- Erreur de chargement -->
      <div v-else-if="erreur" class="alert theme-danger encart" role="alert">
        <p class="texte-encart">{{ texteErreur }}</p>
        <button type="button" class="btn-outline theme-danger btn-styled" @click="charger">
          {{ t('commun.reessayer') }}
        </button>
      </div>

      <!-- Table humeur vide : le formulaire serait inutilisable -->
      <div v-else-if="!humeurs.length" class="alert theme-danger encart" role="alert">
        <p class="texte-encart">{{ t('humeur.form.listeVide') }}</p>
        <button type="button" class="btn-outline theme-danger btn-styled" @click="charger">
          {{ t('commun.reessayer') }}
        </button>
      </div>

      <template v-else>
        <div v-if="humeurToday" class="alert theme-info encart encart-ligne">
          <i class="bi bi-info-circle" aria-hidden="true"></i>
          <div class="encart-contenu">
            <i18n-t keypath="humeur.form.dejaNotee" tag="p" class="texte-encart">
              <template #humeur>
                <strong>{{ libelleHumeur(humeurToday) }}</strong>
              </template>
            </i18n-t>
            <RouterLink v-if="humeurToday.id" :to="`/humeur/${humeurToday.id}`">
              {{ t('humeur.form.voirSaisie') }}
            </RouterLink>
          </div>
        </div>

        <div class="card">
          <div class="card-body">
            <HumeurForm :humeurs :humeur-causes="humeurCauses" :initiale />
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.vue-humeur-form {
  flex: 1 1 auto;
  overflow: auto;
}
.page-formulaire {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 40rem;
  margin-inline: auto;
  padding: 1.5rem 1rem;
}
.lien-retour {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  gap: 0.5rem;
}
.entete-page {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.titre-page {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.2;
}
.date-jour {
  margin: 0;
  color: color-mix(in srgb, currentColor 80%, transparent);
}
.date-jour::first-letter {
  text-transform: uppercase; /* « Samedi 7 novembre » */
}
.etat-chargement {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem 0;
}
.encart {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  margin: 0;
}
.encart-ligne {
  flex-direction: row;
}
.encart-ligne > .bi {
  flex-shrink: 0;
  margin-top: 0.15rem;
}
.encart-contenu {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.texte-encart {
  margin: 0;
}
</style>
