<script setup>
import { computed, inject, nextTick, onBeforeUnmount, ref, watch, watchPostEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Message from '@/components/Message.vue'
import { api, ApiError } from '@/services/api'
import { messageErreur } from '@/utils/erreur'
import {
  demanderReponse,
  marquerLue,
  promesseReponse,
  reponseEnCours,
} from '@/stores/reponsesEnCours'
import NumeroAide from '@/components/NumeroAide.vue'
import AideUrgence from '@/components/AideUrgence.vue'

const alerte = ref(null)

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const rafraichirConversations = inject('rafraichirConversations', () => {})

const conversation = computed(() => (route.params.id ? Number(route.params.id) : null))

// ---------- État ----------
const message = ref('')
const messages = ref([])
/*
 * erreur = { cle, cause?, action? }
 *  - cle    : clé de traduction du message principal
 *  - cause  : l'erreur d'origine, traduite à l'affichage par messageErreur
 *  - action : fonction appelée par « Réessayer »
 * Comme on stocke une clé et pas une phrase, le texte suit les changements de langue.
 */
const erreur = ref(null)
const envoiEnCours = ref(false)
const chargementHistorique = ref(false)
const introuvable = ref(false)
const annonce = ref('')
const enBas = ref(true)

const reponseAttendue = computed(
  () => conversation.value !== null && reponseEnCours(conversation.value)
)
const occupe = computed(() => envoiEnCours.value || reponseAttendue.value)

const texteErreur = computed(() => {
  const e = erreur.value
  if (!e) return ''
  const detail = e.cause ? messageErreur(e.cause) : ''
  return detail ? `${t(e.cle)} ${detail}` : t(e.cle)
})

const zoneMessages = ref(null)
const champ = ref(null)
const titreIntrouvable = ref(null)

const HAUTEUR_MAX = 200
const animationsReduites = window.matchMedia('(prefers-reduced-motion: reduce)').matches
const pointeurPrecis = window.matchMedia('(pointer: fine)').matches

const SUGGESTIONS = [
  { cle: 'respiration', icone: 'bi-wind' },
  { cle: 'stress', icone: 'bi-emoji-frown' },
  { cle: 'sommeil', icone: 'bi-moon' },
  { cle: 'examen', icone: 'bi-lightbulb' },
]
const suggestions = computed(() =>
  SUGGESTIONS.map((s) => ({ ...s, texte: t(`conversation.suggestions.${s.cle}`) }))
)

let idCreeIci = null
let compteur = 0
let dernierChargement = 0
let monte = true
onBeforeUnmount(() => {
  monte = false
})

function estIci(jeton) {
  return monte && jeton === dernierChargement
}

// ---------- Utilitaires ----------
function versMessage(m, idConversation = null) {
  const id = m.id_message ?? m.id
  return {
    cle: `m-${id ?? `x${++compteur}`}`,
    id,
    role: m.role,
    content: m.content,
    id_conversation: m.id_conversation ?? idConversation,
  }
}

function historique() {
  return messages.value
    .filter((m) => !m.enAttente)
    .map(({ role, content }) => ({ role, content }))
}

function estIntrouvable(e) {
  return e instanceof ApiError && e.status === 404
}

async function defiler(anime = true) {
  await nextTick()
  const zone = zoneMessages.value
  if (!zone) return
  zone.scrollTo({ top: zone.scrollHeight, behavior: anime && !animationsReduites ? 'smooth' : 'auto' })
}

function surDefilement() {
  const z = zoneMessages.value
  if (!z) return
  enBas.value = z.scrollHeight - z.scrollTop - z.clientHeight < 80
}

async function focusChamp() {
  if (!pointeurPrecis) return
  await nextTick()
  champ.value?.focus()
}

function ajusterHauteur() {
  const el = champ.value
  if (!el) return
  el.style.height = 'auto'
  const bordures = el.offsetHeight - el.clientHeight
  el.style.height = `${Math.min(el.scrollHeight + bordures, HAUTEUR_MAX)}px`
  el.style.overflowY = el.scrollHeight > HAUTEUR_MAX ? 'auto' : 'hidden'
}
watch(message, () => nextTick(ajusterHauteur))

async function afficherIntrouvable() {
  introuvable.value = true
  erreur.value = null
  envoiEnCours.value = false
  await nextTick()
  titreIntrouvable.value?.focus()
}

// ---------- Réponse de MediMind ----------
function lancerReponse(base) {
  const promesse = demanderReponse(base.id_conversation, () => api.message.traitement(base))
  suivreReponse(base.id_conversation, promesse)
}

async function suivreReponse(idConv, promesse) {
  try {
    const reponse = await promesse
    if (!monte || conversation.value !== idConv || chargementHistorique.value) return

    marquerLue(idConv)
    const msg = versMessage(reponse, idConv)
    if (messages.value.some((m) => m.id === msg.id)) return

    const etaitEnBas = enBas.value
    messages.value.push(msg)
    if (reponse.alerte) alerte.value = reponse.alerte
    annonce.value = t('conversation.arepondu', { contenu: reponse.content })
    if (etaitEnBas) await defiler()
    focusChamp()
  } catch (e) {
    if (!monte || conversation.value !== idConv) return
    console.error(e)
    if (estIntrouvable(e)) return afficherIntrouvable()
    erreur.value = {
      cle: 'conversation.erreurs.reponse',
      cause: e,
      action: () => relancer(idConv),
    }
  }
}

function relancer(idConv) {
  const dernier = messages.value.at(-1)
  if (!dernier || dernier.role !== 'user') return
  erreur.value = null
  lancerReponse({
    message: dernier.content,
    historique: historique().slice(0, -1),
    langue: locale.value, // ← n'est plus 'fr' en dur
    id_conversation: idConv,
  })
}

// ---------- Chargement d'une conversation ----------
async function chargerHistorique(id) {
  const jeton = ++dernierChargement
  introuvable.value = false
  erreur.value = null
  messages.value = []
  envoiEnCours.value = false
  enBas.value = true
  alerte.value = null

  if (id == null) {
    chargementHistorique.value = false
    focusChamp()
    return
  }

  marquerLue(id)
  const reponseAvant = promesseReponse(id)
  chargementHistorique.value = true
  try {
    const corps = await api.message.lister(id)
    if (!estIci(jeton)) return
    messages.value = (corps.data ?? []).map((m) => versMessage(m, id))
    chargementHistorique.value = false

    const attente = reponseAvant ?? promesseReponse(id)
    if (attente) {
      suivreReponse(id, attente)
    } else if (messages.value.at(-1)?.role === 'user') {
      erreur.value = {
        cle: 'conversation.erreurs.pasRepondu',
        action: () => relancer(id),
      }
    }
    await defiler(false)
  } catch (e) {
    if (!estIci(jeton)) return
    console.error(e)
    if (estIntrouvable(e)) return afficherIntrouvable()
    erreur.value = {
      cle: 'conversation.erreurs.chargement',
      cause: e,
      action: () => chargerHistorique(id),
    }
  } finally {
    if (jeton === dernierChargement) chargementHistorique.value = false
  }
}

watch(
  conversation,
  (id) => {
    if (id !== null && id === idCreeIci) {
      idCreeIci = null
      return
    }
    if (!introuvable.value) message.value = ''
    annonce.value = ''
    chargerHistorique(id)
  },
  { immediate: true }
)

// ---------- Envoi ----------
async function envoyerMessage(texte = message.value) {
  const contenu = texte.trim()
  if (!contenu || occupe.value || chargementHistorique.value) return

  erreur.value = null
  annonce.value = ''
  const jeton = dernierChargement
  const idDepart = conversation.value
  const base = {
    message: contenu,
    historique: historique(),
    langue: locale.value,
    id_conversation: idDepart,
  }

  const cleTemp = `tmp-${++compteur}`
  messages.value.push({ cle: cleTemp, role: 'user', content: contenu, enAttente: true })
  message.value = ''
  envoiEnCours.value = true
  await defiler()

  let envoye
  try {
    envoye = await api.message.send(base)
  } catch (e) {
    console.error(e)
    if (!estIci(jeton)) return
    envoiEnCours.value = false
    messages.value = messages.value.filter((m) => m.cle !== cleTemp)
    message.value = contenu
    if (estIntrouvable(e)) return afficherIntrouvable()
    erreur.value = { cle: 'conversation.erreurs.envoi', cause: e }
    focusChamp()
    return
  }

  const idConv = envoye.id_conversation

  if (estIci(jeton)) {
    const i = messages.value.findIndex((m) => m.cle === cleTemp)
    if (i !== -1) messages.value[i] = versMessage(envoye)
    if (idDepart === null) {
      idCreeIci = idConv
      await router.replace({ name: 'conversation', params: { id: idConv } })
    }
  }
  if (idDepart === null) rafraichirConversations()

  lancerReponse({ ...base, id_conversation: idConv })
  if (estIci(jeton)) envoiEnCours.value = false
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault()
    envoyerMessage()
  }
}

const annonceLecteur = computed(() => (occupe.value ? t('conversation.ecrit') : annonce.value))

watchPostEffect(() => {
  const cle = introuvable.value
    ? 'conversation.introuvable.titre'
    : conversation.value ? 'pages.conversation' : 'pages.nouvelleConversation'
  document.title = `${t(cle)} · MediMind`
})
</script>

<template>
  <div class="vue-conversation">
    <h1 class="masque-visuellement">
      {{ conversation ? t('conversation.titre') : t('conversation.titreNouvelle') }}
    </h1>

    <p class="masque-visuellement" aria-live="polite">{{ annonceLecteur }}</p>

    <!-- Conversation introuvable -->
    <section v-if="introuvable" class="etat-vide" aria-labelledby="titre-introuvable">
      <h2 id="titre-introuvable" ref="titreIntrouvable" tabindex="-1">
        {{ t('conversation.introuvable.titre') }}
      </h2>
      <p>{{ t('conversation.introuvable.texte') }}</p>
      <RouterLink :to="{ name: 'conversation' }" class="btn-solid theme-primary btn-styled">
        {{ t('conversation.introuvable.nouvelle') }}
      </RouterLink>
      <i18n-t keypath="aide.besoin" tag="p" class="aide">
        <template #ecoute><NumeroAide type="ecoute" details /></template>
      </i18n-t>
    </section>

    <template v-else>
      <div ref="zoneMessages" class="zone-messages" @scroll.passive="surDefilement">
        <div class="fil" :aria-busy="chargementHistorique">
          <div v-if="chargementHistorique" class="centre">
            <div class="mm-spinner" role="status">
              <span class="masque-visuellement">{{ t('conversation.chargement') }}</span>
            </div>
          </div>

          <div v-else-if="messages.length === 0 && !erreur" class="accueil">
            <div class="logo" aria-hidden="true"><i class="bi bi-chat-heart"></i></div>
            <h2 class="titre-accueil">{{ t('conversation.bonjour') }}</h2>
            <p class="texte-accueil">{{ t('conversation.intro') }}</p>
            <ul class="suggestions">
              <li v-for="s in suggestions" :key="s.cle">
                <button
                  type="button"
                  class="suggestion"
                  :disabled="occupe"
                  @click="envoyerMessage(s.texte)"
                >
                  <i class="bi" :class="s.icone" aria-hidden="true"></i>
                  {{ s.texte }}
                </button>
              </li>
            </ul>
          </div>

          <ol
            v-else-if="messages.length > 0"
            class="liste-messages"
            :aria-label="t('conversation.listeMessages')"
          >
            <li v-for="m in messages" :key="m.cle">
              <Message :message="m" />
            </li>
            <li v-if="occupe" aria-hidden="true">
              <Message :message="{ role: 'assistant', content: '' }" en-cours />
            </li>
          </ol>

          <AideUrgence v-if="alerte" class="alerte-chat" />

          <div v-if="erreur" class="alert theme-danger encadre-erreur" role="alert">
            <p class="texte-erreur">{{ texteErreur }}</p>
            <!-- <button
              v-if="erreur.action"
              type="button"
              class="btn-outline theme-danger btn-styled"
              :disabled="occupe || chargementHistorique"
              @click="erreur.action()"
            >
              {{ t('commun.reessayer') }}
            </button> -->
          </div>
        </div>
      </div>

      <div class="barre-saisie">
        <button
          v-if="!enBas && messages.length > 0"
          type="button"
          class="bouton-bas"
          :title="t('conversation.revenirBas')"
          @click="defiler()"
        >
          <i class="bi bi-arrow-down" aria-hidden="true"></i>
          <span class="masque-visuellement">{{ t('conversation.revenirBas') }}</span>
        </button>

        <form class="fil" @submit.prevent="envoyerMessage()">
          <div class="compositeur">
            <label for="message" class="masque-visuellement">{{ t('conversation.label') }}</label>
            <textarea
              id="message"
              ref="champ"
              v-model="message"
              class="champ-message"
              rows="1"
              :placeholder="t('conversation.placeholder')"
              aria-describedby="aide-saisie"
              @keydown="onKeydown"
            ></textarea>
            <button
              type="submit"
              class="bouton-envoyer"
              :title="t('conversation.envoyer')"
              :disabled="!message.trim() || occupe || chargementHistorique"
            >
              <i class="bi bi-send-fill" aria-hidden="true"></i>
              <span class="masque-visuellement">{{ t('conversation.envoyer') }}</span>
            </button>
          </div>

          <p id="aide-saisie" class="aide raccourci">{{ t('conversation.raccourci') }}</p>
          <i18n-t keypath="aide.pied" tag="p" class="aide">
            <template #ecoute><NumeroAide type="ecoute" /></template>
            <template #urgence><NumeroAide type="urgence" /></template>
          </i18n-t>
        </form>
      </div>
    </template>
  </div>
</template>

<style scoped>
.vue-conversation {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}
.zone-messages {
  flex: 1 1 auto;
  overflow-y: auto;
  overscroll-behavior: contain;
}
.fil {
  width: 100%;
  max-width: 48rem;
  margin-inline: auto;
  padding: 1.5rem 1rem;
}
.centre {
  display: flex;
  justify-content: center;
  padding-block: 3rem;
}

/* --- Accueil --- */
.accueil {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding-block: 3rem 1rem;
}
.logo {
  display: grid;
  place-items: center;
  width: 3.5rem;
  height: 3.5rem;
  margin-bottom: 1rem;
  border-radius: 1rem;
  font-size: 1.75rem;
  color: var(--mm-accent);
  background-color: color-mix(in srgb, var(--mm-accent) 15%, transparent);
}
.titre-accueil {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
}
.texte-accueil {
  margin: 0 0 1.5rem;
  opacity: 0.75;
}
.suggestions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
  gap: 0.5rem;
  width: 100%;
  margin: 0;
  padding: 0;
  list-style: none;
}
.suggestion {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  height: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--mm-bordure);
  border-radius: 0.75rem;
  background-color: var(--mm-surface);
  color: inherit;
  font: inherit;
  text-align: start;
  cursor: pointer;
}
.suggestion i {
  color: var(--mm-accent);
}
.suggestion:hover {
  border-color: var(--mm-accent);
}
.suggestion:focus-visible {
  outline: 3px solid var(--mm-accent);
  outline-offset: 2px;
}
.suggestion:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* --- Messages --- */
.liste-messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

/* --- Erreur --- */
/* --- Erreur --- */
/* .alert est déjà flex dans Bootstrap 6 : on règle l'alignement nous-mêmes */
.encadre-erreur {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  margin-top: 1rem;
}
.texte-erreur {
  flex: 1 1 16rem; /* prend la place disponible, passe au-dessus du bouton si l'écran est étroit */
  min-width: 0;
  margin: 0;
}
.encadre-erreur button {
  flex-shrink: 0;
  margin: 0;
}


/* --- Barre de saisie --- */
.barre-saisie {
  position: relative;
  flex-shrink: 0;
  border-top: 1px solid var(--mm-bordure);
  background-color: var(--mm-surface);
}
.barre-saisie .fil {
  padding-block: 0.75rem;
}
.compositeur {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  padding: 0.375rem 0.375rem 0.375rem 1rem;
  border: 1px solid var(--mm-bordure);
  border-radius: 1.5rem;
  background-color: var(--mm-fond);
}
.compositeur:focus-within {
  border-color: var(--mm-accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--mm-accent) 30%, transparent);
}
@media (forced-colors: active) {
  .compositeur:focus-within {
    outline: 2px solid Highlight;
  }
}
.champ-message {
  flex: 1 1 auto;
  min-width: 0;
  padding: 0.5rem 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  line-height: 1.5;
  resize: none;
  overflow-y: hidden;
}
.bouton-envoyer {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border: 0;
  border-radius: 50%;
  background-color: var(--mm-accent);
  color: light-dark(#ffffff, #0b1a2e);
  cursor: pointer;
}
.bouton-envoyer:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.bouton-envoyer:focus-visible {
  outline: 3px solid var(--mm-accent);
  outline-offset: 2px;
}
.aide {
  margin: 0.5rem 0 0;
  font-size: 0.8125rem;
  text-align: center;
  opacity: 0.75;
}
.aide :deep(a) {
  color: inherit;
  font-weight: 600;
}
/* Deux lignes d'aide qui se suivent : moins d'espace entre elles */
.aide + .aide {
  margin-top: 0.25rem;
}
@media (hover: none) {
  .raccourci {
    display: none;
  }
}
.bouton-bas {
  position: absolute;
  bottom: calc(100% + 0.75rem);
  left: 50%;
  transform: translateX(-50%);
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid var(--mm-bordure);
  border-radius: 50%;
  background-color: var(--mm-surface);
  color: inherit;
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.15);
  cursor: pointer;
}
.bouton-bas:focus-visible {
  outline: 3px solid var(--mm-accent);
  outline-offset: 2px;
}
.alerte-chat {
  margin-top: 1rem;
}
</style>
