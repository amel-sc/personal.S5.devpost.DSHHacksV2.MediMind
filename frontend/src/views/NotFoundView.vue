<script setup>
import { onMounted, ref } from 'vue'

const titre = ref(null)
onMounted(() => titre.value?.focus())
</script>

<template>
  <section class="etat-vide" aria-labelledby="titre-404">
    <h1 id="titre-404" ref="titre" tabindex="-1">Page introuvable</h1>
    <p>Cette adresse ne correspond à aucune page de MediMind.</p>
    <div class="etat-vide-actions">
      <RouterLink :to="{ name: 'conversation' }" class="btn-solid theme-primary btn-styled">
        Démarrer une conversation
      </RouterLink>
      <RouterLink :to="{ name: 'humeurList' }" class="btn-outline theme-primary btn-styled">
        Mon journal d'humeur
      </RouterLink>
    </div>
    <p>Besoin de parler à quelqu'un maintenant ? <a href="tel:3114">3114</a>, gratuit, 24 h/24.</p>
  </section>
</template>
