<script setup>
import { computed, nextTick, ref, useId, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { api } from '@/services/api'
import { messageErreur } from '@/utils/erreur'
import { niveauHumeur, estDifficile, libelleHumeur, libelleCause } from '@/utils/humeur'

const props = defineProps({
  humeurs: { type: Array, required: true },      // table humeur : { id, val, desce }
  humeurCauses: { type: Array, required: true }, // table humeur_cause : { id, val/desce ou cause_val/cause_desce, code }
  // Humeur déjà notée aujourd'hui : { humeur, note, causes: [ids] }
  initiale: { type: Object, default: null },
})

const NOTE_MAX = 500
const CLE_BROUILLON = 'medimind-brouillon-humeur'

const { t } = useI18n()
const uid = useId()
const router = useRouter()

const refFormulaire = ref(null)
const refNote = ref(null)
const refAlerte = ref(null)

/* ---------- Options traduites ---------- */
const options = computed(() =>
  props.humeurs
    .map((o) => ({
      id: o.id,
      val: Number(o.val),
      libelle: libelleHumeur({ humeur_val: o.val, humeur_desce: o.desce }),
      emoji: niveauHumeur(Number(o.val)).emoji,
    }))
    .sort((a, b) => a.val - b.val),
)

// Accepte les deux formats possibles (val/desce ou cause_val/cause_desce)
const optionsCauses = computed(() =>
  props.humeurCauses.map((c) => ({
    id: c.id,
    libelle: libelleCause({
      code: c.code,
      cause_val: c.cause_val ?? c.val,
      cause_desce: c.cause_desce ?? c.desce,
    }),
  })),
)

/* ---------- Valeurs de départ et brouillon ---------- */
function jourLocal(d = new Date()) {
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`
}

// Ne garde que des valeurs qui existent encore (table modifiée, brouillon ancien…)
function nettoyer(v) {
  const valeurs = new Set(options.value.map((o) => o.val))
  const ids = new Set(props.humeurCauses.map((c) => c.id))
  const h = Number(v?.humeur)
  return {
    humeur: valeurs.has(h) ? h : null,
    note: String(v?.note ?? '').slice(0, NOTE_MAX),
    causes: Array.isArray(v?.causes)
      ? [...new Set(v.causes.map(Number))].filter((id) => ids.has(id))
      : [],
  }
}

function signature(v) {
  return JSON.stringify([v.humeur, v.note.trim(), [...v.causes].sort((a, b) => a - b)])
}

function lireBrouillon() {
  try {
    const b = JSON.parse(sessionStorage.getItem(CLE_BROUILLON) ?? 'null')
    if (!b || b.jour !== jourLocal()) {
      sessionStorage.removeItem(CLE_BROUILLON) // brouillon d'un autre jour : on l'oublie
      return null
    }
    return nettoyer(b)
  } catch {
    return null
  }
}

function supprimerBrouillon() {
  try {
    sessionStorage.removeItem(CLE_BROUILLON)
  } catch { /* stockage indisponible : rien à faire */ }
}

const depart = nettoyer(props.initiale)
const brouillon = lireBrouillon()
const source = brouillon ?? depart

const humeur = ref(source.humeur)
const note = ref(source.note)
const causes = ref(source.causes)
const brouillonRestaure = ref(Boolean(brouillon) && signature(brouillon) !== signature(depart))

const modifie = computed(
  () => signature({ humeur: humeur.value, note: note.value, causes: causes.value }) !== signature(depart),
)

const enregistre = ref(false)

watch(
  [humeur, note, causes],
  () => {
    if (enregistre.value) return
    try {
      if (modifie.value) {
        sessionStorage.setItem(
          CLE_BROUILLON,
          JSON.stringify({ jour: jourLocal(), humeur: humeur.value, note: note.value, causes: causes.value }),
        )
      } else {
        sessionStorage.removeItem(CLE_BROUILLON)
      }
    } catch { /* navigation privée stricte, quota… : pas grave */ }
  },
  { deep: true },
)

async function effacerBrouillon() {
  supprimerBrouillon()
  humeur.value = depart.humeur
  note.value = depart.note
  causes.value = [...depart.causes]
  brouillonRestaure.value = false
  tentative.value = false
  // Le bouton disparaît : on remet le focus à un endroit logique
  await nextTick()
  focusHumeur()
}
/* ---------- Validation et erreurs ---------- */
const envoi = ref(false)
const tentative = ref(false)
const erreurGlobale = ref(null)  // objet erreur brut
const erreursServeur = ref({})   // { humeur?, note?, causes? } → clés i18n

const texteErreurGlobale = computed(() =>
  erreurGlobale.value ? messageErreur(erreurGlobale.value) : '',
)

const erreurHumeur = computed(() => {
  if (erreursServeur.value.humeur) return t(erreursServeur.value.humeur)
  if (tentative.value && humeur.value === null) return t('humeur.form.erreurs.humeurRequise')
  return null
})
const erreurNote = computed(() => {
  if (note.value.length > NOTE_MAX) return t('humeur.form.erreurs.noteTropLongue', { max: NOTE_MAX })
  if (erreursServeur.value.note) return t(erreursServeur.value.note)
  return null
})
const erreurCauses = computed(() =>
  erreursServeur.value.causes ? t(erreursServeur.value.causes) : null,
)

// Une erreur serveur disparaît dès que l'utilisateur corrige le champ concerné
watch(humeur, () => { erreursServeur.value = { ...erreursServeur.value, humeur: null } })
watch(note, () => { erreursServeur.value = { ...erreursServeur.value, note: null } })
watch(causes, () => { erreursServeur.value = { ...erreursServeur.value, causes: null } }, { deep: true })

// Associe les erreurs du backend à des messages traduits (pas de texte brut de Pydantic)
function lireErreursServeur(e) {
  const champs = e?.errors ?? {}
  const r = {}
  if (e?.code === 'humeur_inconnue' || champs.id_humeur) r.humeur = 'humeur.form.erreurs.humeurInvalide'
  if (champs.note) r.note = 'humeur.form.erreurs.noteInvalide'
  if (e?.code === 'cause_inconnue' || champs.id_humeur_causes) r.causes = 'humeur.form.erreurs.causesInvalides'
  return r
}

const afficherSoutien = computed(() => humeur.value !== null && estDifficile(humeur.value))

/* ---------- Compteur de caractères ---------- */
const restant = computed(() => NOTE_MAX - note.value.length)
// Ne change qu'aux paliers : la zone live n'annonce pas chaque frappe
const annonceCompteur = computed(() => {
  if (restant.value <= 0) return t('humeur.form.compteurLimite', { max: NOTE_MAX })
  for (const palier of [10, 50]) {
    if (restant.value <= palier) return t('humeur.form.compteurReste', { n: palier })
  }
  return ''
})

/* ---------- Envoi ---------- */
function focusHumeur() {
  const f = refFormulaire.value
  ;(f?.querySelector('input[type="radio"]:checked') ?? f?.querySelector('input[type="radio"]'))?.focus()
}

async function envoyer() {
  if (envoi.value) return

  tentative.value = true
  erreurGlobale.value = null
  erreursServeur.value = {}

  if (humeur.value === null) {
    focusHumeur()
    return
  }
  if (note.value.length > NOTE_MAX) {
    refNote.value?.focus()
    return
  }

  envoi.value = true
  try {
    const reponse = await api.humeurJours.save({
      id_humeur: humeur.value, // le backend attend la valeur (humeur.val)
      note: note.value.trim(),
      id_humeur_causes: causes.value,
    })
    enregistre.value = true
    supprimerBrouillon()
    await router.replace(
      reponse?.id_humeur_jours
        ? {
            path: `/humeur/${reponse.id_humeur_jours}`,
            // Passé dans l'historique du navigateur, pas dans l'URL
            state: { enregistree: props.initiale ? 'maj' : 'nouvelle' },
          }
        : '/humeur/list',
    )

  } catch (e) {
    console.error(e)
    erreurGlobale.value = e
    erreursServeur.value = lireErreursServeur(e)
    await nextTick()
    refAlerte.value?.focus()
  } finally {
    envoi.value = false
  }
}
</script>

<template>
  <form ref="refFormulaire" class="formulaire" novalidate :aria-busy="envoi" @submit.prevent="envoyer">
    <!-- Annonce de l'envoi (le texte du bouton qui change n'est pas toujours lu) -->
    <p class="masque-visuellement" role="status">
      {{ envoi ? t('humeur.form.enregistrement') : '' }}
    </p>

    <!-- Erreur générale : reçoit le focus, donc pas de role="alert" (évite une double lecture) -->
    <div
      v-if="erreurGlobale"
      ref="refAlerte"
      class="alert theme-danger encart-erreur"
      tabindex="-1"
    >
      <i class="bi bi-exclamation-triangle" aria-hidden="true"></i>
      <p class="sans-marge">{{ texteErreurGlobale }}</p>
    </div>

    <!-- Brouillon restauré -->
    <div v-if="brouillonRestaure" class="alert theme-secondary encart-brouillon" role="status">
      <p class="sans-marge">{{ t('humeur.form.brouillon.restaure') }}</p>
      <button type="button" class="btn-text theme-inverse" @click="effacerBrouillon">
        {{ t('humeur.form.brouillon.effacer') }}
      </button>
    </div>

    <!-- 1. Humeur -->
    <fieldset class="groupe" :aria-describedby="erreurHumeur ? `${uid}-err-humeur` : undefined">
      <legend class="legende">
        {{ t('humeur.form.humeurLegende') }}
        <span class="mention">{{ t('humeur.form.obligatoire') }}</span>
      </legend>

      <div
        class="choix-humeur"
        :class="{ invalide: erreurHumeur }"
        :style="{ '--nb': options.length }"
      >
        <div v-for="o in options" :key="o.id" class="option">
          <input
            :id="`${uid}-humeur-${o.val}`"
            v-model="humeur"
            class="input-cache"
            type="radio"
            required
            :name="`${uid}-humeur`"
            :value="o.val"
            :aria-invalid="erreurHumeur ? 'true' : undefined"
          />
          <label :for="`${uid}-humeur-${o.val}`" class="carte-choix">
            <span class="emoji" aria-hidden="true">{{ o.emoji }}</span>
            <span class="libelle-choix">{{ o.libelle }}</span>
          </label>
        </div>
      </div>

      <p v-if="erreurHumeur" :id="`${uid}-err-humeur`" class="message-erreur">
        <i class="bi bi-exclamation-circle" aria-hidden="true"></i>
        {{ erreurHumeur }}
      </p>
    </fieldset>

    <!-- Soutien si « Mal » ou « Très mal » (zone toujours présente pour être annoncée) -->
    <div aria-live="polite">
      <aside v-if="afficherSoutien" class="alert theme-info encart-soutien" :aria-label="t('humeur.form.soutien.label')">
        <p class="sans-marge">{{ t('humeur.form.soutien.texte') }}</p>
        <ul class="liste-soutien">
          <i18n-t keypath="humeur.form.soutien.medimind" tag="li">
            <template #lien>
              <RouterLink :to="{ name: 'conversation' }">{{ t('humeur.form.soutien.lienMedimind') }}</RouterLink>
            </template>
          </i18n-t>
          <i18n-t keypath="humeur.form.soutien.urgence" tag="li">
            <template #numero><a href="tel:3114">3114</a></template>
          </i18n-t>
        </ul>
        <p class="sans-marge petit">{{ t('humeur.form.soutien.conserve') }}</p>
      </aside>
    </div>

    <!-- 2. Note -->
    <div class="groupe">
      <label :for="`${uid}-note`" class="legende">
        {{ t('humeur.form.noteLabel') }}
        <span class="mention">{{ t('humeur.form.facultatif') }}</span>
      </label>
      <textarea
        :id="`${uid}-note`"
        ref="refNote"
        v-model="note"
        class="form-control"
        rows="4"
        :maxlength="NOTE_MAX"
        :placeholder="t('humeur.form.notePlaceholder')"
        :aria-invalid="erreurNote ? 'true' : undefined"
        :aria-describedby="[`${uid}-note-aide`, erreurNote && `${uid}-err-note`].filter(Boolean).join(' ')"
      ></textarea>
      <p :id="`${uid}-note-aide`" class="compteur" :class="{ limite: restant <= 50 }">
        {{ t('humeur.form.compteur', { n: note.length, max: NOTE_MAX }) }}
      </p>
      <p class="masque-visuellement" aria-live="polite">{{ annonceCompteur }}</p>
      <p v-if="erreurNote" :id="`${uid}-err-note`" class="message-erreur">
        <i class="bi bi-exclamation-circle" aria-hidden="true"></i>
        {{ erreurNote }}
      </p>
    </div>

    <!-- 3. Causes (on envoie l'id de humeur_cause) -->
    <fieldset
      class="groupe"
      :aria-describedby="[`${uid}-aide-causes`, erreurCauses && `${uid}-err-causes`].filter(Boolean).join(' ')"
    >
      <legend class="legende">
        {{ t('humeur.form.causesLegende') }}
        <span class="mention">{{ t('humeur.form.facultatif') }}</span>
      </legend>
      <p :id="`${uid}-aide-causes`" class="aide">{{ t('humeur.form.causesAide') }}</p>

      <div class="choix-causes">
        <div v-for="c in optionsCauses" :key="c.id" class="option">
          <input
            :id="`${uid}-cause-${c.id}`"
            v-model="causes"
            class="input-cache"
            type="checkbox"
            :value="c.id"
          />
          <label :for="`${uid}-cause-${c.id}`" class="puce">
            <i class="bi bi-check-lg icone-check" aria-hidden="true"></i>
            {{ c.libelle }}
          </label>
        </div>
      </div>

      <p v-if="erreurCauses" :id="`${uid}-err-causes`" class="message-erreur">
        <i class="bi bi-exclamation-circle" aria-hidden="true"></i>
        {{ erreurCauses }}
      </p>
    </fieldset>

    <!-- Actions -->
    <div class="actions">
      <RouterLink to="/humeur/list" class="btn-text theme-inverse" @click="supprimerBrouillon">
        {{ t('humeur.form.annuler') }}
      </RouterLink>
      <button
        type="submit"
        class="btn-solid theme-primary btn-styled bouton-envoi"
        :class="{ occupe: envoi }"
        :aria-disabled="envoi ? 'true' : undefined"
      >
        <span v-if="envoi" class="mm-spinner mm-spinner-sm" aria-hidden="true"></span>
        {{
          envoi
            ? t('humeur.form.enregistrement')
            : initiale ? t('humeur.form.mettreAJour') : t('humeur.form.enregistrer')
        }}
      </button>
    </div>
  </form>
</template>

<style scoped>
.formulaire {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}
.sans-marge {
  margin: 0;
}
.petit {
  font-size: 0.875rem;
}

/* --- Groupes de champs --- */
.groupe {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
  margin: 0;
  padding: 0;
  border: 0;
}
.legende {
  margin: 0 0 0.25rem;
  padding: 0;
  font-size: 1rem;
  font-weight: 600;
}
.mention {
  font-size: 0.875rem;
  font-weight: 400;
  color: color-mix(in srgb, currentColor 75%, transparent);
}
.aide {
  margin: 0;
  font-size: 0.875rem;
  color: color-mix(in srgb, currentColor 80%, transparent);
}

/* --- Encadrés --- */
.encart-erreur {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin: 0;
}
.encart-erreur:focus-visible {
  outline: 3px solid currentColor;
  outline-offset: 2px;
}
.encart-brouillon {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  margin: 0;
}
.encart-soutien {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 0;
}
.liste-soutien {
  margin: 0;
  padding-left: 1.25rem;
}

/* Input invisible mais toujours focusable au clavier */
.option {
  position: relative;
}
.input-cache {
  position: absolute;
  opacity: 0;
  width: 1px;
  height: 1px;
  margin: 0;
  pointer-events: none;
}

/* --- Sélecteur d'humeur --- */
.choix-humeur {
  display: grid;
  grid-template-columns: repeat(var(--nb, 5), minmax(0, 1fr));
  gap: 0.5rem;
}
.carte-choix {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  height: 100%;
  min-height: 2.75rem;
  padding: 0.75rem 0.25rem;
  border: 2px solid var(--mm-bordure, rgba(127, 127, 127, 0.35));
  border-radius: 0.75rem;
  text-align: center;
  cursor: pointer;
}
.libelle-choix {
  font-size: 0.875rem;
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.carte-choix .emoji {
  font-size: 2rem;
  line-height: 1;
  filter: grayscale(0.6);
  opacity: 0.8;
}
.carte-choix:hover {
  background-color: rgba(127, 127, 127, 0.08);
}
input:checked + .carte-choix {
  border-color: currentColor;
  background-color: rgba(127, 127, 127, 0.15);
  font-weight: 600;
}
input:checked + .carte-choix .emoji {
  filter: none;
  opacity: 1;
}
.choix-humeur.invalide .carte-choix {
  border-style: dashed;
  border-color: light-dark(#b02a37, #f1aeb5);
}

/* Très petits écrans : liste verticale, plus lisible que 5 colonnes serrées */
@media (max-width: 22rem) {
  .choix-humeur {
    grid-template-columns: 1fr;
  }
  .carte-choix {
    flex-direction: row;
    justify-content: flex-start;
    gap: 0.75rem;
    padding: 0.5rem 0.75rem;
    text-align: start;
  }
  .carte-choix .emoji {
    font-size: 1.5rem;
  }
}

/* --- Puces des causes --- */
.choix-causes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.puce {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  min-height: 2.75rem; /* cible tactile confortable */
  padding: 0.375rem 1rem;
  border: 1px solid var(--mm-bordure, rgba(127, 127, 127, 0.35));
  border-radius: 999px;
  cursor: pointer;
}
.puce:hover {
  background-color: rgba(127, 127, 127, 0.08);
}
.puce .icone-check {
  display: none;
}
input:checked + .puce {
  border-color: currentColor;
  background-color: rgba(127, 127, 127, 0.2);
  font-weight: 600;
}
input:checked + .puce .icone-check {
  display: inline; /* l'état ne dépend pas que de la couleur */
}

/* Focus clavier visible */
input:focus-visible + .carte-choix,
input:focus-visible + .puce {
  outline: 3px solid currentColor;
  outline-offset: 2px;
}

/* --- Note --- */
.compteur {
  margin: 0;
  font-size: 0.875rem;
  text-align: end;
  color: color-mix(in srgb, currentColor 75%, transparent);
}
.compteur.limite {
  color: inherit;
  font-weight: 600;
}

/* --- Erreurs --- */
.message-erreur {
  display: flex;
  align-items: flex-start;
  gap: 0.375rem;
  margin: 0;
  font-size: 0.875rem;
  color: light-dark(#b02a37, #f1aeb5); /* lisible en clair et en sombre */
}

/* --- Actions --- */
.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  gap: 0.75rem;
}
.bouton-envoi {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.bouton-envoi.occupe {
  opacity: 0.75;
  cursor: progress;
}
@media (max-width: 36rem) {
  .actions {
    flex-direction: column-reverse;
    align-items: stretch;
  }
  .actions > * {
    justify-content: center;
    text-align: center;
  }
}

/* --- Animations seulement si l'utilisateur les accepte --- */
@media (prefers-reduced-motion: no-preference) {
  .carte-choix {
    transition: border-color 0.15s, background-color 0.15s;
  }
  .carte-choix .emoji {
    transition: transform 0.15s, filter 0.15s, opacity 0.15s;
  }
  input:checked + .carte-choix .emoji {
    transform: scale(1.15);
  }
}

/* --- Contraste élevé (Windows) --- */
@media (forced-colors: active) {
  .carte-choix .emoji {
    filter: none;
    opacity: 1;
  }
  input:checked + .carte-choix,
  input:checked + .puce {
    border-color: Highlight;
    outline: 2px solid Highlight;
  }
}
</style>
