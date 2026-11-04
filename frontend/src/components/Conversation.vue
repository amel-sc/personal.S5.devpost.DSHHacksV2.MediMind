<script setup>
import { ref, nextTick } from 'vue';
import Message from './Message.vue';
import { sendMessage } from '@/services/api.js';

const message = ref('')
const erreur = ref(null)
const chargment = ref(false)
const finConversation = ref(null);

const messages = ref([])

async function scrollToBottom() {
  await nextTick();

  finConversation.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'end'
  });
}

async function envoyerMessage() {
  const contenu = message.value.trim();

  if (!contenu) return;

  messages.value.push({
    sender: 'user',
    content: contenu
  });

  console.log('Message envoyé :', contenu);

  message.value = '';

  // Descendre après l'ajout du message utilisateur
  await scrollToBottom();

  // TODO : envoyer le message au backend et ajouter sa réponse
  try {
    // active loading
    chargment.value = true;

    // Faire apparaître l'indicateur de chargement
    await scrollToBottom();

    const reponse = await sendMessage({
      message: contenu,
      langue: "fr"
    })
    // add reponse in messages
    messages.value.push(reponse)
    
  } catch (e) {
    erreur.value = "Une erreur s'est produite"
  } finally {
    chargment.value = false

    // Descendre après la réponse de MediMind
    await scrollToBottom();
  }
}
</script>

<template>
  <div class="conversation">
      <div v-if="messages.length > 0" class="d-flex flex-column gap-3">
            <Message v-for="item in messages" :message="item" />
      </div>
      <div v-else>
          <p><strong>MediMind</strong> : En quoi puis-je vous aidez en tant qu'assistant psychologique</p>
      </div>
      <div v-if="chargment" class="d-flex justify-content-start mt-3">
        <span class="placeholder-wave fg-3">Traitement des réponses pour vous aidez…</span>
      </div>

      <!-- Repère pour le scroll automatique -->
      <div ref="finConversation"></div>
  </div>

  <div class="fixed-bottom border-top">
    <div class="container py-3">
      <form @submit.prevent="envoyerMessage">
        <div class="row g-2 align-items-end">
          <div class="col">
            <label for="message" class="visually-hidden">
              Écrire un message
            </label>

            <textarea
              id="message"
              v-model="message"
              class="form-control"
              rows="1"
              placeholder="Écrivez votre message..."
            ></textarea>
          </div>

          <div class="col-auto">
            <button
              type="submit"
              class="btn btn-primary"
              aria-label="Envoyer"
              :disabled="!message.trim() || chargment"
            >
              <i class="bi bi-send-fill"></i>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>
<style scoped>
.conversation {
  padding-bottom: 100px;
  padding-top: 100px;
}
</style>