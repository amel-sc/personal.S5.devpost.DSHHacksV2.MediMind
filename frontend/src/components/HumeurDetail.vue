<script setup>
import { computed, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  ECHELLE,
  niveauHumeur,
  estActive,
  versDate,
  libelleHumeur,
  libelleCause,
} from '../utils/humeur'

const props = defineProps({
  afficherMeta: { type: Boolean, default: true },
  humeurJours: { type: Object, default: null },
  humeurJoursCauses: { type: Array, default: () => [] },
  // Remplace le titre calculé (« Ton humeur aujourd'hui » / « Ton humeur du … »)
  titre: { type: String, default: null },
  // Niveau du titre : 2 sous le h1 d'une page, 3 sous un h2, etc.
  niveauTitre: {
    type: Number,
    default: 2,
    validator: (n) => Number.isInteger(n) && n >= 2 && n <= 5,
  },
  // Titre invisible mais lu par les lecteurs d'écran (quand le parent a déjà un titre visible)
  titreMasque: { type: Boolean, default: false },
})

const { t, locale } = useI18n()
const idTitre = useId()

/* ---------- Titres ---------- */
const baliseTitre = computed(() => `h${props.niveauTitre}`)
const baliseSousTitre = computed(() => `h${Math.min(props.niveauTitre + 1, 6)}`)

/* ---------- Niveau d'humeur ---------- */
// Valeurs 1…N, que ECHELLE contienne des nombres ou des objets
const TOTAL = ECHELLE.length
const valeursEchelle = Array.from({ length: TOTAL }, (_, i) => i + 1)

const valeur = computed(() => Number(props.humeurJours?.humeur_val))
const valeurValide = computed(
  () => Number.isInteger(valeur.value) && valeur.value >= 1 && valeur.value <= TOTAL,
)

const apparence = computed(() =>
  valeurValide.value
    ? niveauHumeur(valeur.value)
    : { emoji: '❔', theme: 'theme-secondary' },
)

const libelle = computed(() => libelleHumeur(props.humeurJours))

// Le sens de l'échelle n'est pas évident (1 = très bien) : on le précise aux lecteurs d'écran
const descriptionEchelle = computed(() =>
  t('humeur.detail.echelle', {
    n: valeur.value,
    total: TOTAL,
    min: t('humeur.niveaux.1'),
    max: t(`humeur.niveaux.${TOTAL}`),
  }),
)

/* ---------- Contenu ---------- */
const remplacee = computed(() => Boolean(props.humeurJours) && !estActive(props.humeurJours))
const note = computed(() => String(props.humeurJours?.note ?? '').trim())
const causes = computed(() => (props.humeurJoursCauses ?? []).filter(Boolean))

/* ---------- Date ---------- */
const date = computed(() => {
  const d = versDate(props.humeurJours?.date_creation)
  return d instanceof Date && !Number.isNaN(d.getTime()) ? d : null
})

const estAujourdhui = computed(
  () => date.value?.toDateString() === new Date().toDateString(),
)

const jour = computed(() => {
  if (!date.value) return ''
  const memeAnnee = date.value.getFullYear() === new Date().getFullYear()
  return date.value.toLocaleDateString(locale.value, {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    ...(memeAnnee ? {} : { year: 'numeric' }),
  })
})

const heure = computed(() =>
  date.value
    ? date.value.toLocaleTimeString(locale.value, { hour: 'numeric', minute: '2-digit' })
    : '',
)

const titreAffiche = computed(() => {
  if (props.titre) return props.titre
  if (!date.value) return t('humeur.detail.titre')
  if (estAujourdhui.value) return t('humeur.detail.titreAujourdhui')
  return t('humeur.detail.titreDate', { date: jour.value })
})

// Si le titre visible donne déjà le jour, on n'affiche que l'heure
const texteDate = computed(() => {
  if (!date.value) return ''
  const jourDejaDansTitre = !props.titre && !props.titreMasque
  if (jourDejaDansTitre) return t('humeur.detail.noteeA', { heure: heure.value })
  if (estAujourdhui.value) return t('humeur.detail.noteeAujourdhui', { heure: heure.value })
  return t('humeur.detail.noteeLe', { date: jour.value, heure: heure.value })
})
</script>

<template>
  <article
    v-if="humeurJours"
    class="card card-subtle"
    :class="apparence.theme"
    :aria-labelledby="idTitre"
  >
    <div class="card-body detail-corps">
      <component
        :is="baliseTitre"
        :id="idTitre"
        class="detail-titre"
        :class="{ 'masque-visuellement': titreMasque }"
      >
        {{ titreAffiche }}
      </component>

      <p v-if="afficherMeta && (texteDate || remplacee)" class="detail-meta">
        <time v-if="date" :datetime="date.toISOString()">{{ texteDate }}</time>
        <span v-if="remplacee" class="badge badge-outline theme-secondary badge-remplacee">
          {{ t('journal.remplacee') }}
        </span>
      </p>

      <div class="detail-niveau">
        <span class="detail-emoji" aria-hidden="true">{{ apparence.emoji }}</span>
        <div>
          <p class="detail-libelle">
            {{ libelle }}
            <span v-if="valeurValide" class="masque-visuellement">{{ descriptionEchelle }}</span>
          </p>
          <ol v-if="valeurValide" class="echelle" aria-hidden="true">
            <li
              v-for="v in valeursEchelle"
              :key="v"
              :class="{ actif: v === valeur }"
            >{{ niveauHumeur(v).emoji }}</li>
          </ol>
        </div>
      </div>

      <div v-if="note">
        <component :is="baliseSousTitre" class="detail-sous-titre">
          {{ t('humeur.detail.note') }}
        </component>
        <p class="detail-note">{{ note }}</p>
      </div>

      <div>
        <component :is="baliseSousTitre" class="detail-sous-titre">
          {{ t('humeur.detail.causes') }}
        </component>
        <ul v-if="causes.length" class="detail-causes">
          <li v-for="(cause, i) in causes" :key="cause.id ?? i">
            <span class="badge badge-subtle theme-secondary">{{ libelleCause(cause) }}</span>
          </li>
        </ul>
        <p v-else class="detail-vide">{{ t('humeur.detail.aucuneCause') }}</p>
      </div>
    </div>
  </article>
</template>

<style scoped>
/* .card-body est déjà une colonne flex : il suffit d'ajouter l'espacement */
.detail-corps {
  gap: 1rem;
}

/* Taille fixe : l'apparence reste la même, que la balise soit h2, h3 ou h4 */
.detail-titre {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.3;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 0.875rem;
  color: color-mix(in srgb, currentColor 80%, transparent);
}

.badge-remplacee {
  border-style: dashed;
}

/* Rangée emoji + libellé (div à part, car .card-body est en colonne) */
.detail-niveau {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.detail-emoji {
  flex-shrink: 0;
  font-size: 2.5rem;
  line-height: 1;
}

.detail-libelle {
  margin: 0 0 0.375rem;
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.3;
}

.echelle {
  display: flex;
  gap: 0.375rem;
  margin: 0;
  padding: 0.25rem 0;
  list-style: none;
}

.echelle li {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  font-size: 1.125rem;
  line-height: 1;
  opacity: 0.4;
  filter: grayscale(1);
}

/* L'état actif ne repose pas que sur l'opacité : il a aussi un anneau et un fond */
.echelle li.actif {
  opacity: 1;
  filter: none;
  background: var(--mm-surface);
  outline: 2px solid currentColor;
  outline-offset: 1px;
}

/* Agrandissement et animation seulement si l'utilisateur ne demande pas moins de mouvement */
@media (prefers-reduced-motion: no-preference) {
  .echelle li {
    transition: transform 0.2s ease, opacity 0.2s ease;
  }
  .echelle li.actif {
    transform: scale(1.15);
  }
}

/* Mode contraste élevé (Windows) : opacité et gris n'ont plus de sens, l'anneau reste */
@media (forced-colors: active) {
  .echelle li {
    opacity: 1;
    filter: none;
  }
  .echelle li.actif {
    outline-color: Highlight;
  }
}

.detail-sous-titre {
  margin: 0 0 0.375rem;
  font-size: 1rem;
  font-weight: 600;
}

.detail-note {
  margin: 0;
  white-space: pre-line;
  overflow-wrap: anywhere;
}

.detail-causes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.detail-vide {
  margin: 0;
  color: color-mix(in srgb, currentColor 80%, transparent);
}
</style>
