<script setup>
import { ref } from 'vue';
import Messages from './Messages.vue';

const message = ref('');

const messages = ref([
  {
    sender: 'medimind',
    content: 'Commencez à écrire votre message.'
  },
  {
    sender: 'user',
    content: 'Voici mon premier message.'
  },
  {
    sender: 'medimind',
    content: 'Commencez à écrire votre message.'
  },
  {
    sender: 'user',
    content: 'Voici mon premier message.'
  },
  {
    sender: 'medimind',
    content: 'Commencez à écrire votre message.'
  },
  {
    sender: 'user',
    content: 'Voici mon premier message.'
  },
  {
    sender: 'medimind',
    content: 'Commencez à écrire votre message.'
  },
  {
    sender: 'user',
    content: 'Voici mon premier message.'
  },
  {
    sender: 'medimind',
    content: 'Commencez à écrire votre message.'
  },
  {
    sender: 'user',
    content: 'Voici mon premier message.'
  },
  {
    sender: 'medimind',
    content: 'Commencez à écrire votre message.'
  },
  {
    sender: 'user',
    content: 'Voici mon premier message.'
  },
  {
    sender: 'medimind',
    content: 'Commencez à écrire votre message.'
  },
  {
    sender: 'user',
    content: 'Voici mon premier message.'
  },
  {
    sender: 'medimind',
    content: 'Commencez à écrire votre message.'
  },
  {
    sender: 'user',
    content: 'Voici mon premier message.'
  },
]);

function envoyerMessage() {
  const contenu = message.value.trim();

  if (!contenu) return;

  messages.value.push({
    sender: 'user',
    content: contenu
  });

  console.log('Message envoyé :', contenu);

  // TODO : envoyer le message au backend et ajouter sa réponse

  message.value = '';
}
</script>

<template>
  <div class="conversation">
    <Messages :messages="messages" />
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
              :disabled="!message.trim()"
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