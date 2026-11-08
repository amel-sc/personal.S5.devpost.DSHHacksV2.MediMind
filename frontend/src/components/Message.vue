<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: { type: Object, required: true },
  enCours: { type: Boolean, default: false }, // indicateur « MediMind écrit… »
})

const estUtilisateur = computed(() => props.message.role === 'user')
</script>

<template>
  <article class="message" :class="estUtilisateur ? 'message-user' : 'message-assistant'">
    <div v-if="!estUtilisateur" class="avatar" aria-hidden="true">
      <i class="bi bi-chat-heart-fill"></i>
    </div>

    <div class="bulle" :class="{ 'en-attente': message.enAttente }">
      <!-- Un titre par message : touche H d'un lecteur d'écran pour passer de l'un à l'autre -->
      <h2 class="auteur" :class="{ 'visually-hidden': estUtilisateur }">
        {{ estUtilisateur ? 'Vous' : 'MediMind' }}
      </h2>

      <p v-if="enCours" class="points"><span></span><span></span><span></span></p>
      <p v-else class="contenu">{{ message.content }}</p>

      <p v-if="message.enAttente" class="statut">Envoi…</p>
    </div>
  </article>
</template>

<style scoped>
.message {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
}
.message-user {
  justify-content: flex-end;
}
.avatar {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  color: var(--mm-accent);
  background-color: color-mix(in srgb, var(--mm-accent) 18%, transparent);
}
.bulle {
  max-width: min(36rem, 85%);
  padding: 0.75rem 1rem;
  border-radius: 1.25rem;
  overflow-wrap: anywhere; /* coupe les URL très longues */
}
.message-user .bulle {
  background-color: color-mix(in srgb, var(--mm-accent) 16%, var(--mm-surface));
  border-end-end-radius: 0.375rem;
}
.message-assistant .bulle {
  background-color: var(--mm-surface);
  border: 1px solid var(--mm-bordure);
  border-end-start-radius: 0.375rem;
}
.bulle.en-attente {
  opacity: 0.7;
}
.auteur {
  margin: 0 0 0.25rem;
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.2;
  opacity: 0.8;
}
.contenu {
  margin: 0;
  white-space: pre-wrap; /* garde les retours à la ligne */
}
.statut {
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
  text-align: end;
  opacity: 0.75;
}

/* Trois points qui rebondissent */
.points {
  display: flex;
  gap: 0.3rem;
  margin: 0;
  padding-block: 0.4rem;
}
.points span {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background-color: currentColor;
  opacity: 0.4;
  animation: rebond 1.2s infinite ease-in-out;
}
.points span:nth-child(2) { animation-delay: 0.15s; }
.points span:nth-child(3) { animation-delay: 0.3s; }
@keyframes rebond {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-0.3rem); opacity: 0.9; }
}
@media (prefers-reduced-motion: reduce) {
  .points span { animation: none; }
}
</style>
