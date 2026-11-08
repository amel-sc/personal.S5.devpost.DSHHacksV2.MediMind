<script setup>
import { computed, nextTick, ref, watch, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { api, ApiError } from '@/services/api'
import { messageErreur } from '@/utils/erreur'
import { versDate, estActive, estDifficile } from '@/utils/humeur'
import HumeurDetail from '@/components/HumeurDetail.vue'

const props = defineProps({ id: { type: String, required: true } })

const { t, locale } = useI18n()

const humeurJours = ref(null)
const humeurJoursCauses = ref([])
const chargement = ref(true)
const erreur = ref(null) // objet erreur brut : traduit à l'affichage
const introuvable = ref(false)

const refSucces = ref(null)
const refTitreIntrouvable = ref(null)

const texteErreur = computed(() => (erreur.value ? messageErreur(erreur.value) : ''))

/* ---------- Message après enregistrement (envoyé par HumeurForm) ---------- */
function lireSucces() {
  const etat = window.history.state
  const valeur = etat?.enregistree
  if (valeur !== 'nouvelle' && valeur !== 'maj') return null
  // On l'efface : un rechargement ou un retour en arrière ne le réaffichera pas
  window.history.replaceState({ ...etat, enregistree: null }, '')
  return valeur
}
const succes = ref(lireSucces())

/* ---------- Chargement ---------- */
// Si l'id change vite, on ignore les réponses des anciennes requêtes
let requeteCourante = 0

async function charger() {
  const numero = ++requeteCourante
  chargement.value = true
  erreur.value = null
  introuvable.value = false
  humeurJours.value = null
  humeurJoursCauses.value = []

  // Sécurité : le router filtre déjà les id non numériques
  if (!/^[1-9]\d*$/.test(props.id)) {
    introuvable.value = true
    chargement.value = false
    await focusApresChargement(numero)
    return
  }

  try {
    const reponse = await api.humeurJours.find(props.id)
    if (numero !== requeteCourante) return

    if (!reponse?.humeur_jours) {
      introuvable.value = true // au cas où le backend renverrait 200 + null
    } else {
      humeurJours.value = reponse.humeur_jours
      humeurJoursCauses.value = reponse.humeur_jours_causes ?? []
    }
  } catch (e) {
    if (numero !== requeteCourante) return
    console.error(e)
    if (e instanceof ApiError && e.status === 404) introuvable.value = true
    else erreur.value = e
  } finally {
    if (numero === requeteCourante) chargement.value = false
  }

  await focusApresChargement(numero)
}

// Le contenu remplace le spinner : on place le focus là où c'est utile
async function focusApresChargement(numero) {
  if (numero !== requeteCourante) return
  await nextTick()
  if (introuvable.value) refTitreIntrouvable.value?.focus()
  else if (succes.value && humeurJours.value) refSucces.value?.focus()
}

// Se relance aussi en passant de /humeur/3 à /humeur/5
watch(
  () => props.id,
  (_, ancien) => {
    if (ancien !== undefined) succes.value = null // le message ne concernait que l'humeur précédente
    charger()
  },
  { immediate: true },
)

/* ---------- Dates ---------- */
const date = computed(() => {
  const d = versDate(humeurJours.value?.date_creation)
  return d instanceof Date && !Number.isNaN(d.getTime()) ? d : null
})

const jour = computed(() =>
  date.value
    ? date.value.toLocaleDateString(locale.value, {
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
      })
    : '',
)
const heure = computed(() =>
  date.value
    ? date.value.toLocaleTimeString(locale.value, { hour: 'numeric', minute: '2-digit' })
    : '',
)

const titre = computed(() =>
  date.value ? t('humeur.page.titre', { date: jour.value }) : t('pages.detailHumeur'),
)
const estAujourdhui = computed(
  () => !!date.value && date.value.toDateString() === new Date().toDateString(),
)
const remplacee = computed(() => !!humeurJours.value && !estActive(humeurJours.value))
const difficile = computed(() => estDifficile(humeurJours.value?.humeur_val))

/* ---------- Titre de l'onglet (recalculé aussi au changement de langue) ---------- */
watchEffect(() => {
  let base
  if (chargement.value || erreur.value) base = t('pages.detailHumeur')
  else if (introuvable.value) base = t('humeur.page.introuvable.titre')
  else base = titre.value
  document.title = `${base} · MediMind`
})
</script>

<template>
  <div class="vue-humeur-detail">
    <div class="page-detail">
      <RouterLink to="/humeur/list" class="btn-text theme-inverse lien-retour">
        <i class="bi bi-arrow-left" aria-hidden="true"></i>
        {{ t('humeur.form.retour') }}
      </RouterLink>

      <!-- Chargement -->
      <div v-if="chargement" class="etat-chargement" role="status">
        <span class="mm-spinner" aria-hidden="true"></span>
        <span>{{ t('humeur.page.chargement') }}</span>
      </div>

      <!-- Introuvable -->
      <div v-else-if="introuvable" class="etat-vide">
        <p class="emoji-vide" aria-hidden="true">🔍</p>
        <h1 ref="refTitreIntrouvable" tabindex="-1">{{ t('humeur.page.introuvable.titre') }}</h1>
        <p class="texte-attenue">{{ t('humeur.page.introuvable.texte') }}</p>
        <div class="etat-vide-actions">
          <RouterLink to="/humeur/list" class="btn-solid theme-primary btn-styled">
            {{ t('humeur.page.introuvable.action') }}
          </RouterLink>
        </div>
      </div>

      <!-- Erreur -->
      <template v-else-if="erreur">
        <h1 class="titre-page">{{ t('pages.detailHumeur') }}</h1>
        <div class="alert theme-danger encart" role="alert">
          <p class="sans-marge">{{ texteErreur }}</p>
          <button type="button" class="btn-outline theme-danger btn-styled" @click="charger">
            {{ t('commun.reessayer') }}
          </button>
        </div>
      </template>

      <!-- Contenu -->
      <template v-else-if="humeurJours">
        <!-- Reçoit le focus : pas de role="alert", pour éviter une double lecture -->
        <div
          v-if="succes"
          ref="refSucces"
          class="alert theme-success encart-ligne"
          tabindex="-1"
        >
          <i class="bi bi-check-circle" aria-hidden="true"></i>
          <p class="sans-marge">{{ t(`humeur.page.enregistree.${succes}`) }}</p>
        </div>

        <header class="entete-page">
          <h1 class="titre-page">{{ titre }}</h1>
          <p class="meta">
            <span v-if="date" class="texte-attenue">
              <time :datetime="date.toISOString()">{{ t('humeur.detail.noteeA', { heure }) }}</time>
            </span>
            <span v-if="estAujourdhui" class="badge badge-subtle theme-primary">
              {{ t('humeur.page.aujourdhui') }}
            </span>
            <span v-if="remplacee" class="badge badge-outline theme-secondary badge-remplacee">
              {{ t('journal.remplacee') }}
            </span>
          </p>
        </header>

        <div v-if="remplacee" class="alert theme-secondary encart-ligne">
          <i class="bi bi-info-circle" aria-hidden="true"></i>
          <p class="sans-marge">{{ t('humeur.page.remplacee') }}</p>
        </div>

        <HumeurDetail
          :titre="t('humeur.page.ressenti')"
          :niveau-titre="2"
          :afficher-meta="false"
          :humeur-jours
          :humeur-jours-causes
        />

        <aside v-if="difficile" class="alert theme-info encart-ligne" :aria-label="t('humeur.page.soutien.label')">
          <i class="bi bi-heart" aria-hidden="true"></i>
          <i18n-t keypath="humeur.page.soutien.texte" tag="p" class="sans-marge">
            <template #numero><a href="tel:3114">3114</a></template>
          </i18n-t>
        </aside>

        <div class="actions">
          <RouterLink
            v-if="estAujourdhui && !remplacee"
            to="/humeur/new"
            class="btn-outline theme-primary btn-styled bouton-icone"
          >
            <i class="bi bi-pencil" aria-hidden="true"></i>
            {{ t('journal.mettreAJour') }}
          </RouterLink>
          <RouterLink :to="{ name: 'conversation' }" class="btn-solid theme-primary btn-styled bouton-icone">
            <i class="bi bi-chat-heart" aria-hidden="true"></i>
            {{ t('humeur.page.parler') }}
          </RouterLink>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.vue-humeur-detail {
  flex: 1 1 auto;
  overflow: auto;
}
.page-detail {
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
.sans-marge {
  margin: 0;
}
.texte-attenue {
  color: color-mix(in srgb, currentColor 80%, transparent);
}

/* --- États --- */
.etat-chargement {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem 0;
}
.emoji-vide {
  margin: 0;
  font-size: 3rem;
  line-height: 1;
}

/* --- En-tête --- */
.entete-page {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.titre-page {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.2;
}
.meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 0.875rem;
}
.badge-remplacee {
  border-style: dashed;
}

/* --- Encadrés --- */
.encart {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  margin: 0;
}
.encart-ligne {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin: 0;
}
.encart-ligne > .bi {
  flex-shrink: 0;
  margin-top: 0.15rem;
}
.encart-ligne:focus-visible {
  outline: 3px solid currentColor;
  outline-offset: 2px;
}

/* --- Actions --- */
.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.75rem;
}
.bouton-icone {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
@media (max-width: 36rem) {
  .actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
