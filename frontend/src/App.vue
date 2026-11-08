<script setup>
import { computed, onMounted, provide, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/services/api'
import ThemeSelecteur from '@/components/ThemeSelecteur.vue'
import LangueSelecteur from './components/LangueSelecteur.vue'
import { estNonLue, nombreNonLues, reponseEnCours } from '@/stores/reponsesEnCours'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const route = useRoute()
const conversations = ref([])
const erreur = ref(null)
const chargement = ref(false)
const drawer = ref(null)

// Message lu par les lecteurs d'écran quand une réponse arrive dans une autre conversation
const annonceMenu = ref('')
watch(nombreNonLues, (n, avant) => {
  if (n > avant) annonceMenu.value = 'MediMind a répondu dans une autre conversation.'
})

const libelleMenu = computed(() => t('menu.ouvrir', nombreNonLues.value))

async function charger() {
  chargement.value = true
  erreur.value = null
  try {
    const reponse = await api.conversation.lister()
    conversations.value = reponse.data ?? reponse
  } catch (e) {
    console.error(e)
    erreur.value = 'Impossible de charger tes conversations. Réessaie dans un instant.'
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

onMounted(charger)
</script>

<template>
  <div class="app">
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
      <p class="visually-hidden" aria-live="polite">{{ annonceMenu }}</p>
      <span class="nom-app">MediMind</span>
      <div class="reglages">
        <LangueSelecteur />
        <ThemeSelecteur />
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
        <button type="button" class="btn-close" data-bs-dismiss="drawer" aria-label="Fermer le menu"></button>
      </div>

      <div class="drawer-body corps-menu">
        <nav class="nav-principale" aria-label="Navigation principale">
          <RouterLink
            :to="{ name: 'conversation' }"
            class="btn-text theme-inverse item-menu"
            :class="{ actif: sectionActive === 'nouvelle' }"
            :aria-current="ariaCurrent('nouvelle')"
            @click="fermerDrawer"
          >
            <i class="bi bi-plus-lg" aria-hidden="true"></i>
            <span class="texte-tronque">Nouvelle conversation</span>
          </RouterLink>
          <RouterLink
            :to="{ name: 'humeurList' }"
            class="btn-text theme-inverse item-menu"
            :class="{ actif: sectionActive === 'humeur' }"
            :aria-current="ariaCurrent('humeur', route.name === 'humeurList')"
            @click="fermerDrawer"
          >
            <i class="bi bi-journal-text" aria-hidden="true"></i>
            <span class="texte-tronque">Journal d'humeur</span>
          </RouterLink>
        </nav>

        <hr class="separateur" />

        <!-- Chargement -->
        <div v-if="chargement" class="centre-menu">
          <div class="spinner-border spinner-sm" role="status">
            <span class="visually-hidden">Chargement des conversations…</span>
          </div>
        </div>

        <!-- Erreur -->
        <div v-else-if="erreur" class="alert theme-danger erreur-menu" role="alert">
          <p class="texte-erreur">{{ erreur }}</p>
          <button type="button" class="btn-outline theme-danger btn-styled" @click="charger">
            Réessayer
          </button>
        </div>

        <!-- Liste vide -->
        <p v-else-if="conversations.length === 0" class="liste-vide">
          Aucune conversation pour l'instant.
        </p>

        <!-- Liste des conversations -->
        <nav v-else class="liste-conversations" aria-label="Mes conversations">
          <RouterLink
            v-for="c in conversations"
            :key="c.id"
            :to="{ name: 'conversation', params: { id: c.id } }"
            class="btn-text theme-inverse item-menu"
            :class="{ actif: sectionActive === `conversation-${c.id}` }"
            :aria-current="ariaCurrent(`conversation-${c.id}`)"
            :title="c.first_message"
            @click="fermerDrawer"
          >
            <i class="bi bi-chat-left-text" aria-hidden="true"></i>
            <span class="texte-tronque">{{ c.first_message || 'Conversation sans titre' }}</span>

            <template v-if="reponseEnCours(c.id)">
              <span class="spinner-border spinner-sm indicateur" aria-hidden="true"></span>
              <span class="visually-hidden">, MediMind est en train de répondre</span>
            </template>
            <template v-else-if="estNonLue(c.id)">
              <span class="pastille" aria-hidden="true"></span>
              <span class="visually-hidden">, nouvelle réponse</span>
            </template>
          </RouterLink>
        </nav>
      </div>
    </dialog>

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
  opacity: 0.75;
}
.liste-conversations {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  overflow-y: auto;
  min-height: 0;
}

/* Lien pleine largeur, icône et texte alignés à gauche */
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
/* Lien actif : fond, gras ET barre d'accent (pas seulement une nuance de gris) */
.item-menu.actif {
  font-weight: 600;
  background-color: color-mix(in srgb, var(--mm-accent) 15%, transparent);
  box-shadow: inset 3px 0 0 var(--mm-accent);
}
.item-menu.actif i {
  color: var(--mm-accent);
}
/* Mode contraste élevé : les fonds et ombres disparaissent, on garde un repère */
@media (forced-colors: active) {
  .item-menu.actif {
    outline: 2px solid Highlight;
  }
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
.indicateur {
  flex-shrink: 0;
  width: 0.875rem;
  height: 0.875rem;
}
@media (forced-colors: active) {
  .pastille {
    background-color: Highlight;
  }
}

</style>
