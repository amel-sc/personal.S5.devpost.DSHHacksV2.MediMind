<script setup>
import { ref } from 'vue';

const message = ref('');

function envoyerMessage() {
  if (!message.value.trim()) return;

  console.log('Message envoyé :', message.value);

  // TODO : envoyer le message à ton backend / MediMind
  message.value = '';
}
</script>

<template>
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