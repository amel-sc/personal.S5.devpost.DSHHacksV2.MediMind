<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, provide, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { api } from '@/services/api'
import ThemeSelecteur from '@/components/ThemeSelecteur.vue'
import LangueSelecteur from '@/components/LangueSelecteur.vue'
import { estNonLue, nombreNonLues, reponseEnCours } from '@/stores/reponsesEnCours'
import PaysSelecteur from './components/PaysSelecteur.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const conversations = ref([])
const erreur = ref(null) // objet erreur brut (le texte affiché est traduit)
const chargement = ref(false)
const drawer = ref(null)

const utilisateur = ref(null)
const chargementUtilisateur = ref(true)
const erreurDeconnexion = ref(null)

// function to get utilisateur in session
async function chargerUtilisateur() {
  chargementUtilisateur.value = true

  try {
    const reponse = await api.auth.moi()
    utilisateur.value = reponse?.user ?? null

    if (utilisateur.value) {
      await charger()
    } else {
      conversations.value = []
    }
  } catch (e) {
    if (e.status !== 401) console.error(e)
    utilisateur.value = null
    conversations.value = []
  } finally {
    chargementUtilisateur.value = false
  }
}

provide('chargerUtilisateur', chargerUtilisateur)

// function de disconnect
async function deconnecter() {
  erreurDeconnexion.value = null

  try {
    await api.auth.deconnexion()
    utilisateur.value = null
    conversations.value = []
    erreur.value = null
    await router.replace({ name: 'connexion' })
  } catch (e) {
    console.error(e)
    erreurDeconnexion.value = t('auth.erreurDeconnexion')
  }
}

/* ---------- Bouton du menu ---------- */
// 3 formes : 0 → « Ouvrir le menu », 1 → « … (1 nouvelle réponse) », n → « … (n nouvelles réponses) »
const libelleMenu = computed(() => t('menu.ouvrir', nombreNonLues.value))

/* ---------- Annonce pour les lecteurs d'écran ---------- */
// On garde la CLÉ : le texte suit la langue choisie
const cleAnnonce = ref('')
let minuteurAnnonce = null

watch(nombreNonLues, async (n, avant) => {
  if (n <= avant) return
  clearTimeout(minuteurAnnonce)
  // Vider puis remplir : sinon un texte identique n'est pas relu
  cleAnnonce.value = ''
  await nextTick()
  cleAnnonce.value = 'menu.annonce'
  // Effacée ensuite pour ne pas rester lisible dans la page
  minuteurAnnonce = setTimeout(() => { cleAnnonce.value = '' }, 5000)
})

onBeforeUnmount(() => clearTimeout(minuteurAnnonce))

/* ---------- Conversations ---------- */
async function charger() {
  chargement.value = true
  erreur.value = null
  try {
    const reponse = await api.conversation.lister()
    conversations.value = reponse?.data ?? reponse ?? []
  } catch (e) {
    console.error(e)
    erreur.value = e
  } finally {
    chargement.value = false
  }
}

/*
 * Lien actif du menu. Une seule valeur, donc un seul lien actif à la fois :
 *  - 'nouvelle'        → /conversation (sans id)
 *  - 'conversation-5'  → /conversation/5
 *  - 'humeur'          → toutes les pages du journal d'humeur
 *  - null              → page 404
 */
const sectionActive = computed(() => {
  if (route.name === 'conversation') {
    return route.params.id ? `conversation-${route.params.id}` : 'nouvelle'
  }
  if (route.meta.section === 'humeur') return 'humeur'
  return null
})

const estPageAuth = computed(() =>
  ['connexion', 'inscription'].includes(route.name)
)

/*
 * aria-current :
 *  - "page" quand le lien mène exactement à la page affichée ;
 *  - "true" quand on est dans la section (ex. : /humeur/3 pour « Journal d'humeur »).
 */
function ariaCurrent(cle, pageExacte = true) {
  if (sectionActive.value !== cle) return undefined
  return pageExacte ? 'page' : 'true'
}

// ConversationView appelle cette fonction après avoir créé une conversation
provide('rafraichirConversations', charger)

function fermerDrawer() {
  drawer.value?.close()
}

onMounted(chargerUtilisateur)
</script>

<template>
  <div class="app">
    <template v-if="!estPageAuth">
      <header class="entete-app">
        <button
          class="btn-text theme-inverse bouton-menu"
          type="button"
          data-bs-toggle="drawer"
          data-bs-target="#menuMediMind"
          aria-controls="menuMediMind"
          :aria-label="libelleMenu"
        >
          <i class="bi bi-list icone-menu" aria-hidden="true"></i>
          <span v-if="nombreNonLues > 0" class="pastille pastille-menu" aria-hidden="true"></span>
        </button>
        <p class="masque-visuellement" aria-live="polite">{{ cleAnnonce ? t(cleAnnonce) : '' }}</p>
        <span class="nom-app">MediMind</span>
        <div class="reglages">
          <LangueSelecteur />
          <ThemeSelecteur />

          <div v-if="utilisateur" class="bloc-utilisateur">
            <span class="avatar-utilisateur" aria-hidden="true">
              {{ (utilisateur.first_name || utilisateur.email || '?').charAt(0).toUpperCase() }}
            </span>

            <span class="nom-utilisateur">
              {{ utilisateur.first_name || utilisateur.email }}
            </span>

            <button
              type="button"
              class="btn-outline theme-primary bouton-deconnexion"
              :disabled="chargementUtilisateur"
              @click="deconnecter"
            >
              <i class="bi bi-box-arrow-right" aria-hidden="true"></i>
              <span>{{ t('auth.deconnexion') }}</span>
            </button>
          </div>
        </div>
      </header>
  
      <!-- Menu latéral gauche -->
      <dialog
        id="menuMediMind"
        ref="drawer"
        class="drawer drawer-start"
        tabindex="-1"
        aria-labelledby="menuTitre"
      >
        <div class="drawer-header">
          <h2 id="menuTitre" class="drawer-title titre-menu">MediMind</h2>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="drawer"
            :aria-label="t('menu.fermer')"
          ></button>
        </div>
  
        <div class="drawer-body corps-menu">
          <nav class="nav-principale" :aria-label="t('menu.navigation')">
            <RouterLink
              :to="{ name: 'conversation' }"
              class="btn-text theme-inverse item-menu"
              :class="{ actif: sectionActive === 'nouvelle' }"
              :aria-current="ariaCurrent('nouvelle')"
              @click="fermerDrawer"
            >
              <i class="bi bi-plus-lg" aria-hidden="true"></i>
              <span class="texte-tronque">{{ t('menu.nouvelle') }}</span>
            </RouterLink>
            <RouterLink
              :to="{ name: 'humeurList' }"
              class="btn-text theme-inverse item-menu"
              :class="{ actif: sectionActive === 'humeur' }"
              :aria-current="ariaCurrent('humeur', route.name === 'humeurList')"
              @click="fermerDrawer"
            >
              <i class="bi bi-journal-text" aria-hidden="true"></i>
              <span class="texte-tronque">{{ t('menu.journal') }}</span>
            </RouterLink>
          </nav>
  
          <hr class="separateur" />
  
          <!-- Chargement -->
          <div v-if="chargement" class="centre-menu" role="status">
            <span class="mm-spinner mm-spinner-sm" aria-hidden="true"></span>
            <span class="masque-visuellement">{{ t('menu.chargement') }}</span>
          </div>
  
          <!-- Erreur -->
          <div v-else-if="erreur" class="alert theme-danger erreur-menu" role="alert">
            <p class="texte-erreur">{{ t('menu.erreur') }}</p>
            <button type="button" class="btn-outline theme-danger btn-styled" @click="charger">
              {{ t('commun.reessayer') }}
            </button>
          </div>
  
          <!-- Liste vide -->
          <p v-else-if="conversations.length === 0" class="liste-vide">
            {{ t('menu.vide') }}
          </p>
  
          <!-- Liste des conversations -->
          <nav v-else class="liste-conversations" :aria-label="t('menu.mesConversations')">
            <RouterLink
              v-for="c in conversations"
              :key="c.id"
              :to="{ name: 'conversation', params: { id: c.id } }"
              class="btn-text theme-inverse item-menu"
              :class="{ actif: sectionActive === `conversation-${c.id}` }"
              :aria-current="ariaCurrent(`conversation-${c.id}`)"
              :title="c.first_message || undefined"
              @click="fermerDrawer"
            >
              <i class="bi bi-chat-left-text" aria-hidden="true"></i>
              <!-- Texte écrit par l'étudiant : sa langue peut différer de celle de l'interface -->
              <span class="texte-tronque" dir="auto">{{ c.first_message || t('menu.sansTitre') }}</span>
  
              <template v-if="reponseEnCours(c.id)">
                <span class="mm-spinner mm-spinner-sm" aria-hidden="true"></span>
                <span class="masque-visuellement">{{ t('menu.enCours') }}</span>
              </template>
              <template v-else-if="estNonLue(c.id)">
                <span class="pastille" aria-hidden="true"></span>
                <span class="masque-visuellement">{{ t('menu.nonLue') }}</span>
              </template>
            </RouterLink>
          </nav>
        </div>
        <div class="pied-menu">
          <PaysSelecteur />
        </div>
      </dialog>
    </template>

    <main class="contenu">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
/* --- Structure de la page --- */
.app {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
}
.entete-app {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--mm-bordure);
  flex-shrink: 0;
}
.nom-app {
  font-size: 1.25rem;
  font-weight: 600;
}
.reglages {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-inline-start: auto;
}
.icone-menu {
  font-size: 1.5rem;
  line-height: 1;
}
.contenu {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

/* --- Menu --- */
.titre-menu {
  margin: 0;
  font-size: 1.25rem;
}
.corps-menu {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-height: 0;
}
.nav-principale {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.separateur {
  margin-block: 0.25rem;
}
.centre-menu {
  flex: 1 1 auto;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-block: 1rem;
}
.erreur-menu {
  margin: 0;
}
.texte-erreur {
  margin: 0 0 0.5rem;
}
.liste-vide {
  margin: 0;
  font-size: 0.875rem;
  text-align: center;
  color: color-mix(in srgb, currentColor 80%, transparent);
}
.liste-conversations {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  overflow-y: auto;
  min-height: 0;
}

/* Lien pleine largeur, icône et texte alignés au début */
.item-menu {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  min-width: 0;
  justify-content: flex-start;
  text-align: start;
}
/* Texte sur une seule ligne, terminé par « … » s'il est trop long */
.texte-tronque {
  flex: 1 1 auto;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
/* Lien actif : fond, gras ET barre d'accent (pas seulement une nuance) */
/* Survol et lien actif : exactement le même aspect */
.item-menu:is(:hover, .actif) {
  background-color: color-mix(in srgb, currentColor 10%, transparent);
  box-shadow: none;
}
.item-menu:focus-visible {
  outline: 3px solid var(--mm-accent);
  outline-offset: -3px;
}

.bouton-menu {
  position: relative;
}
.pastille {
  flex-shrink: 0;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background-color: var(--mm-accent);
}
.pastille-menu {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  outline: 2px solid var(--mm-fond); /* détache la pastille de l'icône */
}

/* Mode contraste élevé : fonds et ombres disparaissent, on garde des repères */
@media (forced-colors: active) {
  .item-menu.actif {
    outline: 2px solid Highlight;
  }
  .pastille {
    background-color: Highlight;
  }
}
.pied-menu {
  flex-shrink: 0;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--mm-bordure);
}
.bloc-utilisateur {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.avatar-utilisateur {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background-color: color-mix(in srgb, var(--mm-accent) 15%, transparent);
  color: var(--mm-accent);
  font-weight: 700;
}

.nom-utilisateur {
  max-width: 10rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.9rem;
  font-weight: 600;
}

.bouton-deconnexion {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 2.25rem;
  padding-inline: 0.7rem;
}

.bouton-deconnexion:focus-visible {
  outline: 3px solid var(--mm-accent);
  outline-offset: 2px;
}

@media (max-width: 48rem) {
  .nom-utilisateur {
    display: none;
  }

  .bouton-deconnexion span {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    margin: -1px !important;
    padding: 0 !important;
    overflow: hidden !important;
    clip-path: inset(50%) !important;
    white-space: nowrap !important;
    border: 0 !important;
  }

  .bouton-deconnexion {
    width: 2.5rem;
    justify-content: center;
    padding-inline: 0;
  }
}

@media (forced-colors: active) {
  .avatar-utilisateur {
    border: 1px solid ButtonText;
    background: Canvas;
    color: ButtonText;
  }
}
</style>
