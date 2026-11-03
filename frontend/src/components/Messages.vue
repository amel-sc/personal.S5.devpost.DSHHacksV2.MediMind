<script setup>
defineProps({
  messages: {
    type: Array,
    default: () => []
  }
});
</script>

<template>
  <div class="d-flex flex-column gap-3">
    <div
      v-for="(message, index) in messages"
      :key="index"
      class="d-flex"
      :class="message.sender === 'user'
        ? 'justify-content-end'
        : 'justify-content-start'"
    >
      <div
        class="message-bubble p-3 rounded"
        :class="message.sender === 'user'
          ? 'bg-primary text-white'
          : 'bg-light text-dark'"
      >
        <div class="small fw-bold mb-1">
          {{ message.sender === 'user' ? 'Vous' : 'MediMind' }}
        </div>

        <p class="mb-0">{{ message.content }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-bubble {
  max-width: 75%;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}
</style>