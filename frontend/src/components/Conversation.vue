<script setup>
import { ref, nextTick } from 'vue';
import Message from './Message.vue';
import { sendMessage, traitementMessage } from '@/services/api.js';

const message = ref('');
const conversation = ref(null);
const erreur = ref(null);
const chargement = ref(false);
const messages = ref([]);
const zoneMessages = ref(null);

async function scrollToBottom() {
  await nextTick(); // attend que Vue ait affiché le nouveau message
  const zone = zoneMessages.value;
  zone?.scrollTo({ top: zone.scrollHeight, behavior: 'smooth' });
}

async function envoyerMessage() {
  const contenu = message.value.trim();
  if (!contenu || chargement.value) return;

  erreur.value = null;
  messages.value.push({ role: 'user', content: contenu });
  message.value = '';

  chargement.value = true;
  await scrollToBottom();

  try {
    const data = {
      message: contenu,
      historique: messages.value.map((m) => ({ id: m.id, role: m.role, content: m.content, id_conversation: m.id_conversation })),
      langue: 'fr',
      conversation: conversation
    }
    // send message 
    const send_response = await sendMessage(data);
    conversation.value = send_response.id_conversation;
    addMessage(send_response);
    
    // get response from medimind
    data.conversation = send_response.conversation.value;
    const traitement_response = await traitementMessage(data)
    addMessage(traitement_response);

  } catch (e) {
    erreur.value = "Une erreur s'est produite. Réessayez dans un instant.";
  } finally {
    chargement.value = false;
    await scrollToBottom();
  }
}

// function to add new messages in messages
function addMessage(data) {
  messages.value.push({ id: data.id_message, role: data.role, content: data.content, id_conversation: data.id_conversation });
}

// Entrée = envoyer, Maj + Entrée = retour à la ligne
function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    envoyerMessage();
  }
}
</script>

<template>
  <!-- overflow-hidden : empêche la zone de grandir au lieu de défiler (remplace min-height: 0) -->
  <div class="flex-grow-1 d-flex flex-column overflow-hidden">

    <!-- Zone qui défile -->
    <div ref="zoneMessages" class="flex-grow-1 overflow-auto">
      <div class="container py-4">

        <div v-if="messages.length > 0" class="d-flex flex-column gap-3">
          <Message v-for="(item, i) in messages" :key="i" :message="item" />
        </div>

        <div v-else class="text-center text-secondary py-5">
          <h2 class="h4 text-body">MediMind</h2>
          <p class="mb-0">En quoi puis-je vous aider aujourd'hui ?</p>
        </div>

        <div v-if="chargement" class="d-flex align-items-center gap-2 text-secondary small mt-3">
          <span class="spinner-grow spinner-grow-sm" aria-hidden="true"></span>
          <span role="status">MediMind réfléchit…</span>
        </div>

        <div v-if="erreur" class="alert alert-danger mt-3 mb-0" role="alert">{{ erreur }}</div>
      </div>
    </div>

    <!-- Barre de saisie -->
    <div class="border-top bg-body-tertiary flex-shrink-0">
      <div class="container py-3">
        <form @submit.prevent="envoyerMessage">
          <div class="row g-2 align-items-end">
            <div class="col">
              <label for="message" class="visually-hidden">Écrire un message</label>
              <textarea
                id="message"
                v-model="message"
                class="form-control"
                rows="1"
                placeholder="Écrivez votre message..."
                @keydown="onKeydown"
              ></textarea>
            </div>
            <div class="col-auto">
              <button
                type="submit"
                class="btn btn-primary px-4"
                :disabled="!message.trim() || chargement"
              >
                Envoyer
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>