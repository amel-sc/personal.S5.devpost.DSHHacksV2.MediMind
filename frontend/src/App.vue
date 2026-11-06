<script setup>
import { onMounted, ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './services/api'

const route = useRoute()
const conversations = ref([])
const erreur = ref(null)
const chargement = ref(false)
const drawer = ref(null)

async function charger() {
  chargement.value = true
  erreur.value = null
  try {
    const response = await api.conversation.lister();
    conversations.value = response.data
  } catch (e) {
    erreur.value = "Une erreur s'est produite. Réessayez dans un instant."
    console.error(e)
  } finally {
    chargement.value = false
  }
}

// Conversation active déduite de l'URL
const conversationActive = computed(() =>
  route.params.id ? Number(route.params.id) : null
)

watch(conversationActive, (id) => {
  // some vérifie si au moins un élément d'un tableau satisfait une condition
  if (id !== null && !conversations.value.some((c) => c.id === id)) charger()
})

function closeDrawer() {
  drawer.value?.close()
}

onMounted(charger)
</script>

<template>
  <div class="position-fixed top-0 bottom-0 start-0 end-0 d-flex flex-column">
    <header class="d-flex align-items-center gap-3 px-3 py-2 border-bottom flex-shrink-0">
      <button
        class="btn-text theme-inverse"
        type="button"
        data-bs-toggle="drawer"
        data-bs-target="#menuMediMind"
        aria-controls="menuMediMind"
        aria-label="Ouvrir le menu"
      >
        <i class="bi bi-list icone-menu" aria-hidden="true"></i>
      </button>
      <span class="fs-5 fw-semibold">MediMind</span>
    </header>

    <!-- Menu latéral gauche -->
    <dialog ref="drawer" class="drawer drawer-start" tabindex="-1" id="menuMediMind"
            aria-labelledby="menuTitre">
      <div class="drawer-header">
        <h5 class="drawer-title" id="menuTitre">MediMind</h5>
        <button type="button" class="btn-close" data-bs-dismiss="drawer" aria-label="Fermer"></button>
      </div>

      <div class="drawer-body d-flex flex-column gap-2">
        <RouterLink :to="{ name: 'conversation' }" class="btn-text theme-inverse item-conversation" @click="closeDrawer">
          <i class="bi bi-plus-lg" aria-hidden="true"></i>
          <span class="texte-tronque">Nouvelle conversation</span>
        </RouterLink>
        <RouterLink :to="{ name: 'humeur' }" class="btn-text theme-inverse item-conversation" @click="closeDrawer">
          <i class="bi bi-journal-text" aria-hidden="true"></i>
          <span class="texte-tronque">Humeur</span>
        </RouterLink>

        <hr class="my-1">

        <!-- Chargement -->
        <div v-if="chargement" class="flex-grow-1 d-flex justify-content-center align-items-center">
          <div class="spinner-border spinner-sm" role="status">
            <span class="visually-hidden">Chargement…</span>
          </div>
        </div>

        <!-- Erreur -->
        <div v-else-if="erreur" class="alert alert-danger mb-0" role="alert">
          {{ erreur }}
          <button type="button" class="btn-text theme-inverse mt-2" @click="charger">Réessayer</button>
        </div>

        <!-- Liste vide -->
        <p v-else-if="conversations.length === 0" class="small text-center mb-0 opacity-75">
          Aucune conversation pour l'instant.
        </p>

        <!-- Liste des conversations -->
        <nav v-else class="d-flex flex-column gap-1 liste-conversations" aria-label="Conversations">
          <RouterLink
            v-for="c in conversations"
            :key="c.id"
            :to="{ name: 'conversation', params: { id: c.id } }"
            class="btn-text theme-inverse item-conversation"
            :class="{ active: c.id === conversationActive }"
            :title="c.first_message"
            @click="closeDrawer"
          >
            <i class="bi bi-chat-left-text" aria-hidden="true"></i>
            <span class="texte-tronque">{{ c.first_message || 'Conversation sans titre' }}</span>
          </RouterLink>
        </nav>
      </div>
    </dialog>

    <main class="flex-grow-1 d-flex flex-column overflow-hidden">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.icone-menu {
  font-size: 1.5rem;
  line-height: 1;
}

/* Bouton qui prend toute la largeur, icône + texte alignés à gauche */
.item-conversation {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  min-width: 0;
  justify-content: flex-start;
  text-align: start;
}

/* Texte sur une ligne, terminé par "…" s'il est trop long */
.texte-tronque {
  flex: 1 1 auto;
  min-width: 0;            /* indispensable dans un flex */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Conversation ouverte : bien visible */
.item-conversation.active {
  font-weight: 600;
  background-color: rgba(127, 127, 127, 0.15);
}

/* La liste défile si elle est longue */
.liste-conversations {
  overflow-y: auto;
  min-height: 0;
}
</style>
