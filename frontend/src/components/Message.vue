<script setup>
defineProps({
  message: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <div class="d-flex">
    <!-- col-11 / col-md-9 joue le rôle du max-width: 75% ; ms-auto pousse à droite -->
    <div
      class="col-11 col-md-9 d-flex"
      :class="message.role === 'user' ? 'ms-auto justify-content-end' : ''"
    >
      <div
        class="p-3 rounded-3 text-break"
        :class="message.role === 'user'
          ? 'bg-primary text-white'
          : 'bg-body-secondary text-body'"
      >
        <div class="small fw-semibold mb-1">
          {{ message.role === 'user' ? 'Vous' : 'MediMind' }}
        </div>

        <p class="mb-0" style="white-space: pre-wrap">{{ message.content }}</p>
      </div>
    </div>
  </div>
</template>