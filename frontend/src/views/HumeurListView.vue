<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { api, ApiError } from '@/services/api'
import { messageErreur } from '@/utils/erreur'
import { niveauHumeur, estDifficile, estActive, versDate } from '@/utils/humeur'
import HumeurDetail from '@/components/HumeurDetail.vue'
import NumeroAide from '@/components/NumeroAide.vue'

const { t, te, locale } = useI18n()
const route = useRoute()
const router = useRouter()

const JOUR = 24 * 60 * 60 * 1000
const PERIODES = ['7', '30', '90', 'tout']

// ---------- État ----------
const humeurJours = ref([])
const today = ref(null) // { humeur_jours, humeur_jours_causes } | null
const etatToday = ref('chargement') // 'chargement' | 'note' | 'vide' | 'erreur'
const chargement = ref(true)
const erreurListe = ref(null) // erreur d'origine : traduite à l'affichage
const afficherRemplacees = ref(false)
const filtreModifie = ref(false) // l'annonce aria-live n'est lue qu'après une action

// La période vit dans l'URL : elle survit au passage par la page détail
const periode = computed({
  get: () => (PERIODES.includes(route.query.periode) ? route.query.periode : '30'),
  set: (v) => {
    filtreModifie.value = true
    router.replace({ query: { ...route.query, periode: v === '30' ? undefined : v } })
  },
})

// ---------- Chargement ----------
async function charger() {
  chargement.value = true
  erreurListe.value = null
  etatToday.value = 'chargement'

  // En parallèle : si "today" échoue, la liste s'affiche quand même
  const [liste, jour] = await Promise.allSettled([
    api.humeurJours.lister(),
    api.humeurJours.today(),
  ])

  if (liste.status === 'fulfilled') {
    humeurJours.value = liste.value?.data ?? []
  } else {
    console.error(liste.reason)
    erreurListe.value = liste.reason
  }

  if (jour.status === 'fulfilled') {
    today.value = jour.value?.humeur_jours ? jour.value : null
    etatToday.value = today.value ? 'note' : 'vide'
  } else if (jour.reason instanceof ApiError && jour.reason.status === 404) {
    today.value = null // « rien de noté aujourd'hui », pas une erreur
    etatToday.value = 'vide'
  } else {
    console.error(jour.reason)
    today.value = null
    etatToday.value = 'erreur'
  }

  chargement.value = false
}

// ---------- Libellés et dates ----------
function libelleHumeur(h) {
  const cle = `humeur.niveaux.${h.humeur_val}`
  if (h.humeur_val != null && te(cle)) return t(cle)
  return h.humeur_desce ?? t('journal.nonRenseignee')
}

const formatMois = computed(
  () => new Intl.DateTimeFormat(locale.value, { month: 'long', year: 'numeric' })
)
const formatDate = computed(
  () =>
    new Intl.DateTimeFormat(locale.value, {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      hour: '2-digit',
      minute: '2-digit',
    })
)
function dateLisible(valeur) {
  const d = versDate(valeur)
  return d ? formatDate.value.format(d) : t('journal.dateInconnue')
}

const horodatage = (h) => versDate(h.date_creation)?.getTime() ?? 0

// ---------- Filtrage ----------
// Le backend trie déjà par date_creation DESC
const humeursPeriode = computed(() => {
  if (periode.value === 'tout') return humeurJours.value
  const limite = Date.now() - Number(periode.value) * JOUR
  return humeurJours.value.filter((h) => horodatage(h) >= limite)
})
const actives = computed(() => humeursPeriode.value.filter(estActive))
const nbRemplacees = computed(() => humeursPeriode.value.length - actives.value.length)
const visibles = computed(() => (afficherRemplacees.value ? humeursPeriode.value : actives.value))

const groupes = computed(() => {
  const map = new Map()
  for (const h of visibles.value) {
    const d = versDate(h.date_creation)
    const cle = d ? `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}` : 'inconnue'
    if (!map.has(cle)) {
      map.set(cle, {
        cle,
        libelle: d ? formatMois.value.format(d) : t('journal.dateInconnue'),
        items: [],
      })
    }
    map.get(cle).items.push(h)
  }
  return [...map.values()]
})

// Les stats ne portent QUE sur les humeurs actives (une par jour)
const stats = computed(() => {
  const compte = new Map()
  for (const h of actives.value) {
    if (h.humeur_val == null) continue
    const c = compte.get(h.humeur_val) ?? { h, n: 0 }
    c.n++
    compte.set(h.humeur_val, c)
  }
  return {
    total: actives.value.length,
    difficiles: actives.value.filter((h) => estDifficile(h.humeur_val)).length,
    plusFrequente: [...compte.values()].sort((a, b) => b.n - a.n)[0]?.h ?? null,
  }
})

// 3 dernières humeurs actives difficiles, ET toutes dans les 7 derniers jours
const humeursBassesRecentes = computed(() => {
  const limite = Date.now() - 7 * JOUR
  const dernieres = humeurJours.value.filter(estActive).slice(0, 3)
  return (
    dernieres.length === 3 &&
    dernieres.every((h) => estDifficile(h.humeur_val) && horodatage(h) >= limite)
  )
})

const annonce = computed(() =>
  filtreModifie.value && !chargement.value ? t('journal.affichees', visibles.value.length) : ''
)

onMounted(charger)
</script>

<template>
  <div class="defilement">
    <div class="page-humeur">
      <!-- En-tête -->
      <header class="entete">
        <h1 class="titre-page">{{ t('journal.titre') }}</h1>
        <p class="sous-titre">{{ t('journal.sousTitre') }}</p>
      </header>

      <p class="masque-visuellement" aria-live="polite">{{ annonce }}</p>

      <!-- Soutien -->
      <aside v-if="humeursBassesRecentes" class="alert theme-info soutien" :aria-label="t('journal.soutien.label')">
        <p class="soutien-titre">{{ t('journal.soutien.titre') }}</p>
        <p class="soutien-texte">{{ t('journal.soutien.texte') }}</p>
        <div class="actions">
          <RouterLink :to="{ name: 'conversation' }" class="btn-outline theme-primary btn-styled">
            <i class="bi bi-chat-heart" aria-hidden="true"></i> {{ t('journal.soutien.parler') }}
          </RouterLink>
        </div>
        <i18n-t keypath="aide.pied" tag="p" class="aide-soutien">
          <template #ecoute><NumeroAide type="ecoute" details /></template>
          <template #urgence><NumeroAide type="urgence" /></template>
        </i18n-t>
      </aside>

      <!-- Aujourd'hui -->
      <section class="bloc" aria-labelledby="titre-aujourdhui" :aria-busy="etatToday === 'chargement'">
        <h2 id="titre-aujourdhui" class="titre-section">{{ t('journal.aujourdhui') }}</h2>

        <div v-if="etatToday === 'chargement'" class="carte-jour centre">
          <div class="mm-spinner spinner-sm" role="status">
            <span class="masque-visuellement">{{ t('commun.chargement') }}</span>
          </div>
        </div>

        <template v-else-if="etatToday === 'note'">
          <HumeurDetail
            :humeur-jours="today.humeur_jours"
            :humeur-jours-causes="today.humeur_jours_causes"
            :niveau-titre="3" 
            titre-masque
          />
          <RouterLink :to="{ name: 'humeurCreate' }" class="btn-outline theme-primary btn-styled lien-maj">
            <i class="bi bi-pencil" aria-hidden="true"></i> {{ t('journal.mettreAJour') }}
          </RouterLink>
        </template>

        <div v-else-if="etatToday === 'vide'" class="carte-jour carte-vide">
          <span class="emoji-grand" aria-hidden="true">🌱</span>
          <div class="texte-vide">
            <p class="libelle">{{ t('journal.pasEncore') }}</p>
            <p class="secondaire">{{ t('journal.pasEncoreAide') }}</p>
          </div>
          <RouterLink :to="{ name: 'humeurCreate' }" class="btn-solid theme-primary btn-styled">
            <i class="bi bi-plus-lg" aria-hidden="true"></i> {{ t('journal.noter') }}
          </RouterLink>
        </div>

        <div v-else class="alert theme-danger" role="alert">
          <p class="texte-alerte">{{ t('journal.erreurAujourdhui') }}</p>
          <div class="actions">
            <button type="button" class="btn-outline theme-danger btn-styled" @click="charger">
              {{ t('commun.reessayer') }}
            </button>
            <RouterLink :to="{ name: 'humeurCreate' }" class="btn-text theme-primary">
              {{ t('journal.noter') }}
            </RouterLink>
          </div>
        </div>
      </section>

      <!-- Historique -->
      <section class="bloc" aria-labelledby="titre-historique" :aria-busy="chargement">
        <div class="entete-historique">
          <h2 id="titre-historique" class="titre-section">{{ t('journal.historique') }}</h2>
          <div class="filtres">
            <div class="champ-filtre">
              <label for="filtre-periode" class="label-filtre">{{ t('journal.periode.label') }}</label>
              <select id="filtre-periode" v-model="periode" class="form-control">
                <option v-for="p in PERIODES" :key="p" :value="p">{{ t(`journal.periode.${p}`) }}</option>
              </select>
            </div>
            <label v-if="nbRemplacees > 0" class="case">
              <input
                v-model="afficherRemplacees"
                type="checkbox"
                @change="filtreModifie = true"
              />
              {{ t('journal.afficherRemplacees', { n: nbRemplacees }) }}
            </label>
          </div>
        </div>

        <!-- Chargement -->
        <div v-if="chargement" class="centre bloc-centre">
          <div class="mm-spinner" role="status">
            <span class="masque-visuellement">{{ t('journal.chargement') }}</span>
          </div>
        </div>

        <!-- Erreur -->
        <div v-else-if="erreurListe" class="alert theme-danger" role="alert">
          <p class="texte-alerte">{{ t('journal.erreurListe') }} {{ messageErreur(erreurListe) }}</p>
          <button type="button" class="btn-outline theme-danger btn-styled" @click="charger">
            {{ t('commun.reessayer') }}
          </button>
        </div>

        <!-- Vide -->
        <div v-else-if="visibles.length === 0" class="etat-vide">
          <p class="emoji-grand" aria-hidden="true">🌱</p>
          <p>{{ humeurJours.length === 0 ? t('journal.aucune') : t('journal.aucunePeriode') }}</p>
          <button
            v-if="humeurJours.length > 0 && periode !== 'tout'"
            type="button"
            class="btn-text theme-primary"
            @click="periode = 'tout'"
          >
            {{ t('journal.toutAfficher') }}
          </button>
        </div>

        <!-- Liste -->
        <template v-else>
          <dl class="stats" :aria-label="t('journal.stats.label')">
            <div class="card stat">
              <dt class="stat-libelle">{{ t('journal.stats.entrees') }}</dt>
              <dd class="stat-valeur">{{ stats.total }}</dd>
            </div>
            <div v-if="stats.plusFrequente" class="card stat">
              <dt class="stat-libelle">{{ t('journal.stats.frequente') }}</dt>
              <dd class="stat-valeur">
                <span aria-hidden="true">{{ niveauHumeur(stats.plusFrequente.humeur_val).emoji }}</span>
                {{ libelleHumeur(stats.plusFrequente) }}
              </dd>
            </div>
            <div class="card stat">
              <dt class="stat-libelle">{{ t('journal.stats.difficiles') }}</dt>
              <dd class="stat-valeur">{{ stats.difficiles }}</dd>
            </div>
          </dl>

          <section
            v-for="groupe in groupes"
            :key="groupe.cle"
            :aria-labelledby="`mois-${groupe.cle}`"
            class="mois"
          >
            <h3 :id="`mois-${groupe.cle}`" class="titre-mois">{{ groupe.libelle }}</h3>
            <ul class="liste">
              <li v-for="h in groupe.items" :key="h.id">
                <RouterLink
                  :to="{ name: 'humeurDetail', params: { id: h.id } }"
                  class="card carte-humeur"
                  :class="[`niveau-${h.humeur_val}`, { remplacee: !estActive(h) }]"
                >
                  <div class="ligne-humeur">
                    <span class="emoji-liste" aria-hidden="true">{{ niveauHumeur(h.humeur_val).emoji }}</span>
                    <div class="texte-carte">
                      <p class="libelle tronque">{{ libelleHumeur(h) }}</p>
                      <p v-if="h.note" class="secondaire tronque">{{ h.note }}</p>
                      <time :datetime="h.date_creation" class="date">{{ dateLisible(h.date_creation) }}</time>
                    </div>
                    <span v-if="!estActive(h)" class="badge badge-outline theme-secondary">
                      {{ t('journal.remplacee') }}
                    </span>
                    <i class="bi bi-chevron-right chevron" aria-hidden="true"></i>
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
/* --- Structure --- */
.defilement {
  flex: 1 1 auto;
  overflow-y: auto;
}
.page-humeur {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 48rem;
  margin-inline: auto;
  padding: 1.5rem 1rem 3rem;
}
.entete {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.titre-page {
  margin: 0;
  font-size: 1.75rem;
}
.sous-titre {
  margin: 0;
  opacity: 0.8;
}
.bloc {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.titre-section {
  margin: 0;
  font-size: 1.25rem;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.centre {
  display: flex;
  justify-content: center;
  align-items: center;
}
.bloc-centre {
  padding-block: 3rem;
}
.texte-alerte {
  margin: 0 0 0.5rem;
}

/* --- Soutien --- */
.soutien {
  margin: 0;
}
.soutien-titre {
  margin: 0 0 0.25rem;
  font-weight: 600;
}
.soutien-texte {
  margin: 0 0 0.75rem;
}
.aide-soutien {
  margin: 0.75rem 0 0;
  font-size: 0.875rem;
  line-height: 1.45;
}
.aide-soutien :deep(a) {
  color: inherit;
  font-weight: 600;
}

/* --- Aujourd'hui --- */
.carte-jour {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border: 1px solid var(--mm-bordure);
  border-radius: 0.75rem;
  background-color: var(--mm-surface);
}
.carte-vide {
  flex-wrap: wrap;
  border-style: dashed;
}
.texte-vide {
  flex: 1 1 14rem;
  min-width: 0;
}
.lien-maj {
  align-self: flex-start;
}
.emoji-grand {
  margin: 0;
  font-size: 2rem;
  line-height: 1;
}

/* --- Filtres --- */
.entete-historique {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}
.filtres {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 1rem;
}
.champ-filtre {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.label-filtre {
  font-size: 0.875rem;
}
.case {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 2.5rem; /* cible tactile confortable */
  font-size: 0.875rem;
  cursor: pointer;
}
.case input {
  width: 1.125rem;
  height: 1.125rem;
  accent-color: var(--mm-accent);
}

/* --- Stats --- */
.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 0;
}
.stat {
  flex: 1 1 9rem;
  padding: 0.5rem 1rem;
}
.stat-libelle {
  font-size: 0.875rem;
  font-weight: 400;
  opacity: 0.8;
}
.stat-valeur {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

/* --- Liste --- */
.mois {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.titre-mois {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  opacity: 0.8;
}
.titre-mois::first-letter {
  text-transform: uppercase; /* « novembre 2026 » → « Novembre 2026 » */
}
.liste {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 0;
  padding: 0;
  list-style: none;
}
.carte-humeur {
  color: inherit;
  text-decoration: none;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.carte-humeur.remplacee {
  border-style: dashed;
}
.ligne-humeur {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 1rem;
}
.emoji-liste {
  flex-shrink: 0;
  font-size: 1.75rem;
  line-height: 1;
}
.texte-carte {
  flex: 1 1 auto;
  min-width: 0;
}
.libelle {
  margin: 0;
  font-weight: 600;
}
.secondaire {
  margin: 0;
  font-size: 0.875rem;
}
.date {
  font-size: 0.875rem;
  opacity: 0.8;
}
.tronque {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.badge,
.chevron {
  flex-shrink: 0;
}
.chevron {
  opacity: 0.6;
}
.carte-humeur:hover {
  transform: translateY(-1px);
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.08);
}
.carte-humeur:focus-visible {
  outline: 3px solid var(--mm-accent);
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