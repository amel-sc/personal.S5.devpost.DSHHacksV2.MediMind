<script setup>
import { computed, inject, nextTick, onBeforeUnmount, ref, watch, watchPostEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Message from '@/components/Message.vue'
import { api, ApiError } from '@/services/api'
import { messageErreur } from '@/utils/erreur'
import {
  demanderReponse,
  marquerLue,
  promesseReponse,
  reponseEnCours,
} from '@/stores/reponsesEnCours'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const rafraichirConversations = inject('rafraichirConversations', () => {})

const conversation = computed(() => (route.params.id ? Number(route.params.id) : null))

// ---------- État ----------
const message = ref('')
const messages = ref([])
const erreur = ref(null) // { texte, action? } — action est une fonction
const envoiEnCours = ref(false) // enregistrement du message de l'utilisateur
const chargementHistorique = ref(false)
const introuvable = ref(false)
const annonce = ref('')
const enBas = ref(true)

// L'attente de réponse dépend de la conversation AFFICHÉE, pas d'un booléen global
const reponseAttendue = computed(
  () => conversation.value !== null && reponseEnCours(conversation.value)
)
const occupe = computed(() => envoiEnCours.value || reponseAttendue.value)

const zoneMessages = ref(null)
const champ = ref(null)
const titreIntrouvable = ref(null)

const HAUTEUR_MAX = 200
const animationsReduites = window.matchMedia('(prefers-reduced-motion: reduce)').matches
const pointeurPrecis = window.matchMedia('(pointer: fine)').matches

// Les suggestions deviennent un computed : elles changent avec la langue
const suggestions = computed(() => [
  { icone: 'bi-wind', texte: t('conversation.suggestions.respiration') },
  { icone: 'bi-emoji-frown', texte: t('conversation.suggestions.stress') },
  { icone: 'bi-moon', texte: t('conversation.suggestions.sommeil') },
  { icone: 'bi-lightbulb', texte: t('conversation.suggestions.examen') },
])

// La langue envoyée au LLM suit l'interface (c'était 'fr' en dur à deux endroits)
const { locale } = useI18n()

let idCreeIci = null
let compteur = 0
let dernierChargement = 0 // augmente à chaque changement réel de conversation
let monte = true
onBeforeUnmount(() => {
  monte = false
})

// L'utilisateur regarde-t-il toujours ce qu'il regardait au moment du jeton ?
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

// Affiche la réponse SEULEMENT si l'utilisateur regarde encore cette conversation
async function suivreReponse(idConv, promesse) {
  try {
    const reponse = await promesse
    if (!monte || conversation.value !== idConv || chargementHistorique.value) return
    // Sinon : la réponse est en base, il la verra en revenant

    marquerLue(idConv)
    const msg = versMessage(reponse, idConv)
    if (messages.value.some((m) => m.id === msg.id)) return // déjà là (chargée avec l'historique)

    const etaitEnBas = enBas.value
    messages.value.push(msg)
    annonce.value = t('conversation.arepondu', { contenu: reponse.content })
    if (etaitEnBas) await defiler()
    focusChamp()
  } catch (e) {
    if (!monte || conversation.value !== idConv) return
    console.error(e)
    if (estIntrouvable(e)) return afficherIntrouvable()
    erreur.value = {
      texte: `MediMind n'a pas pu répondre. ${messageErreur(e)}`,
      action: () => relancer(idConv),
    }
  }
}

// Redemande une réponse au dernier message de l'utilisateur
function relancer(idConv) {
  const dernier = messages.value.at(-1)
  if (!dernier || dernier.role !== 'user') return
  erreur.value = null
  lancerReponse({
    message: dernier.content,
    historique: historique().slice(0, -1), // tout sauf ce dernier message
    langue: 'fr',
    id_conversation: idConv,
  })
}

// ---------- Chargement d'une conversation ----------
async function chargerHistorique(id) {
  const jeton = ++dernierChargement
  introuvable.value = false
  erreur.value = null
  messages.value = []
  envoiEnCours.value = false // l'envoi éventuel concernait l'ancienne conversation
  enBas.value = true

  if (id == null) {
    chargementHistorique.value = false
    focusChamp()
    return
  }

  marquerLue(id)
  // Capturée AVANT la requête : si la réponse arrive pendant le chargement, on ne la rate pas
  const reponseAvant = promesseReponse(id)
  chargementHistorique.value = true
  try {
    const corps = await api.message.lister(id)
    if (!estIci(jeton)) return
    messages.value = (corps.data ?? []).map((m) => versMessage(m, id))
    chargementHistorique.value = false

    const attente = reponseAvant ?? promesseReponse(id)
    if (attente) {
      suivreReponse(id, attente) // une réponse est en route : l'indicateur s'affiche
    } else if (messages.value.at(-1)?.role === 'user') {
      // Dernier message sans réponse (erreur pendant qu'il était ailleurs, rechargement…)
      erreur.value = {
        texte: "MediMind n'a pas répondu à ton dernier message.",
        action: () => relancer(id),
      }
    }
    await defiler(false)
  } catch (e) {
    if (!estIci(jeton)) return
    console.error(e)
    if (estIntrouvable(e)) return afficherIntrouvable()
    erreur.value = {
      texte: `Impossible de charger la conversation. ${messageErreur(e)}`,
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
      idCreeIci = null // conversation créée ici : les messages sont déjà affichés
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
  // Historique capturé MAINTENANT, sans le nouveau message : il ne change plus ensuite
  const base = { message: contenu, historique: historique(), langue: locale.value, id_conversation: idDepart }

  // 1. Affichage immédiat
  const cleTemp = `tmp-${++compteur}`
  messages.value.push({ cle: cleTemp, role: 'user', content: contenu, enAttente: true })
  message.value = ''
  envoiEnCours.value = true
  await defiler()

  // 2. Enregistrement
  let envoye
  try {
    envoye = await api.message.send(base)
  } catch (e) {
    console.error(e)
    if (!estIci(jeton)) return // il est ailleurs : rien à afficher
    envoiEnCours.value = false
    messages.value = messages.value.filter((m) => m.cle !== cleTemp)
    message.value = contenu
    if (estIntrouvable(e)) return afficherIntrouvable()
    erreur.value = {
      texte: `Ton message n'a pas été envoyé (il a été remis dans la zone de saisie). ${messageErreur(e)}`,
    }
    focusChamp()
    return
  }

  const idConv = envoye.id_conversation

  if (estIci(jeton)) {
    const i = messages.value.findIndex((m) => m.cle === cleTemp)
    if (i !== -1) messages.value[i] = versMessage(envoye)
    // On ne change l'URL QUE s'il est toujours sur cet écran (sinon on le ramènerait de force)
    if (idDepart === null) {
      idCreeIci = idConv
      await router.replace({ name: 'conversation', params: { id: idConv } })
    }
  }
  if (idDepart === null) rafraichirConversations()

  // 3. Réponse demandée MÊME s'il est parti : elle sera en base à son retour
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
// annonce.value = t('conversation.arepondu', { contenu: reponse.content })

watchPostEffect(() => {
  const cle = introuvable.value
    ? 'pages.conversationIntrouvable'
    : conversation.value ? 'pages.conversation' : 'pages.nouvelleConversation'
  document.title = `${t(cle)} · MediMind` // se met à jour tout seul au changement de langue
})
</script>

<template>
  <div class="vue-conversation">
    <h1 class="visually-hidden">
      {{ conversation ? 'Conversation avec MediMind' : 'Nouvelle conversation avec MediMind' }}
    </h1>

    <p class="visually-hidden" aria-live="polite">{{ annonceLecteur }}</p>

    <section v-if="introuvable" class="etat-vide" aria-labelledby="titre-introuvable">
      <h2 id="titre-introuvable" ref="titreIntrouvable" tabindex="-1">Conversation introuvable</h2>
      <p>
        Ce lien ne correspond à aucune conversation : l'adresse est peut-être incorrecte,
        ou la conversation n'existe plus. Tes autres conversations sont toujours dans le menu.
      </p>
      <RouterLink :to="{ name: 'conversation' }" class="btn-solid theme-primary btn-styled">
        Nouvelle conversation
      </RouterLink>
      <p>Besoin de parler à quelqu'un maintenant ? <a href="tel:3114">3114</a>, gratuit, 24 h/24.</p>
    </section>

    <template v-else>
      <div ref="zoneMessages" class="zone-messages" @scroll.passive="surDefilement">
        <div class="fil" :aria-busy="chargementHistorique">
          <div v-if="chargementHistorique" class="centre">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Chargement de la conversation…</span>
            </div>
          </div>

          <div v-else-if="messages.length === 0 && !erreur" class="accueil">
            <div class="logo" aria-hidden="true"><i class="bi bi-chat-heart"></i></div>
            <h2 class="titre-accueil">{{ t('conversation.bonjour') }}</h2>
            <p class="texte-accueil">
              Un espace pour parler de ce que tu ressens, sans jugement.
              Par quoi veux-tu commencer ?
            </p>
            <ul class="suggestions">
              <li v-for="s in suggestions" :key="s.texte">
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

          <ol v-else-if="messages.length > 0" class="liste-messages" aria-label="Messages de la conversation">
            <li v-for="m in messages" :key="m.cle">
              <Message :message="m" />
            </li>
            <!-- Uniquement si CETTE conversation attend une réponse -->
            <li v-if="occupe" aria-hidden="true">
              <Message :message="{ role: 'assistant', content: '' }" en-cours />
            </li>
          </ol>

          <div v-if="erreur" class="alert theme-danger encadre-erreur" role="alert">
            <p class="texte-erreur">{{ erreur.texte }}</p>
            <button
              v-if="erreur.action"
              type="button"
              class="btn-outline theme-danger btn-styled"
              :disabled="occupe || chargementHistorique"
              @click="erreur.action()"
            >
              Réessayer
            </button>
          </div>
        </div>
      </div>

      <div class="barre-saisie">
        <button
          v-if="!enBas && messages.length > 0"
          type="button"
          class="bouton-bas"
          title="Revenir aux derniers messages"
          @click="defiler()"
        >
          <i class="bi bi-arrow-down" aria-hidden="true"></i>
          <span class="visually-hidden">Revenir aux derniers messages</span>
        </button>

        <form class="fil" @submit.prevent="envoyerMessage()">
          <div class="compositeur">
            <label for="message" class="visually-hidden">Ton message à MediMind</label>
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
              title="Envoyer"
              :disabled="!message.trim() || occupe || chargementHistorique"
            >
              <i class="bi bi-send-fill" aria-hidden="true"></i>
              <span class="visually-hidden">Envoyer</span>
            </button>
          </div>

          <p id="aide-saisie" class="aide raccourci">
            Entrée pour envoyer · Maj + Entrée pour aller à la ligne
          </p>
          <p class="aide">
            MediMind ne remplace pas un professionnel de santé.
            En cas d'urgence : <a href="tel:3114">3114</a> (prévention du suicide, 24h/24)
            ou <a href="tel:112">112</a>.
          </p>
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
.encadre-erreur {
  margin-top: 1rem;
}
.texte-erreur {
  margin: 0;
}
.encadre-erreur button {
  margin-top: 0.5rem;
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
.aide a {
  color: inherit;
  font-weight: 600;
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
</style>
