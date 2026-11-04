<script setup>
import Conversation from './components/Conversation.vue';
</script>

<template>
  <!-- position-fixed + top/bottom 0 = hauteur exacte de l'écran visible, y compris sur mobile -->
  <div class="position-fixed top-0 bottom-0 start-0 end-0 d-flex flex-column">
    <nav class="navbar flex-shrink-0">
      <div class="container-fluid">
        <span class="navbar-brand mb-0 h1">MediMind</span>
      </div>
    </nav>

    <Conversation />
  </div>
</template>