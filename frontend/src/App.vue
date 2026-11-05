<script setup>
import Conversation from './components/Conversation.vue';
</script>

<template>
  <!-- position-fixed + top/bottom 0 = hauteur exacte de l'écran visible, y compris sur mobile -->
  <div class="position-fixed top-0 bottom-0 start-0 end-0 d-flex flex-column">
    <header class="d-flex align-items-center gap-3 px-3 py-2 border-bottom flex-shrink-0">
      <button
        class="btn-text theme-inverse"
        type="button"
        data-bs-toggle="drawer"
        data-bs-target="#menuMediMind"
        aria-controls="menuMediMind"
      >
        <i 
          class="bi bi-list"
        >
      </i>
      </button>
      <span class="fs-5 fw-semibold">MediMind</span>
    </header>

    <!-- Menu latéral gauche -->
    <dialog class="drawer drawer-start" tabindex="-1" id="menuMediMind"
            aria-labelledby="menuTitre">
      <div class="drawer-header">
        <h5 class="drawer-title" id="menuTitre">MediMind</h5>
        <button type="button" class="btn-close" data-bs-dismiss="drawer"
                aria-label="Fermer"></button>
      </div>

      <div class="drawer-body d-flex flex-column gap-2">
        <button type="button" class="btn-solid theme-primary"
                data-bs-dismiss="drawer" @click="nouvelleConversation">
          + Nouvelle conversation
        </button>

        <hr>
      </div>
    </dialog>

    <Conversation />
  </div>
</template>