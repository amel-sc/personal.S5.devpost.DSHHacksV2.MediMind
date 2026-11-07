<script setup>
import { computed, useId } from 'vue'
import { NOTE_MAX, niveauNote } from '@/utils/humeur'

const props = defineProps({
  humeurJours: { type: Object, default: null },
  humeurJoursCauses: { type: Array, default: () => [] },
  titre: { type: String, default: "Votre humeur aujourd'hui" },
})

const idTitre = useId() // id unique même si le composant est affiché plusieurs fois
const niveau = computed(() => niveauNote(props.humeurJours?.note))
const aDesCauses = computed(() => props.humeurJoursCauses?.length > 0)
</script>

<template>
  <article
    v-if="humeurJours"
    class="card card-subtle"
    :class="niveau?.theme"
    :aria-labelledby="idTitre"
  >
    <div class="card-body">
      <h2 :id="idTitre" class="h5 mb-3">{{ titre }}</h2>

      <div class="d-flex align-items-center gap-3 mb-3">
        <span class="emoji-humeur" aria-hidden="true">{{ niveau?.emoji ?? '📝' }}</span>
        <div class="flex-grow-1">
          <p class="fs-5 fw-semibold mb-1">{{ humeurJours.humeur_desce }}</p>

          <template v-if="typeof humeurJours.note === 'number'">
            <label :for="`${idTitre}-note`" class="small">
              Note : <strong>{{ humeurJours.note }}</strong> sur {{ NOTE_MAX }}
              <span v-if="niveau"> ({{ niveau.label }})</span>
            </label>
            <meter
              :id="`${idTitre}-note`"
              class="jauge-note"
              min="0"
              :max="NOTE_MAX"
              :value="humeurJours.note"
            ></meter>
          </template>
        </div>
      </div>

      <h3 class="h6 mb-2">Ce qui a influencé votre humeur</h3>
      <ul v-if="aDesCauses" class="list-unstyled d-flex flex-wrap gap-2 mb-0">
        <li v-for="cause in humeurJoursCauses" :key="cause.id">
          <span class="badge badge-subtle theme-secondary">{{ cause.cause_val }}</span>
        </li>
      </ul>
      <p v-else class="mb-0 opacity-75">Aucune cause renseignée.</p>
    </div>
  </article>
</template>

<style scoped>
.emoji-humeur {
  font-size: 2.5rem;
  line-height: 1;
}
.jauge-note {
  display: block;
  width: 100%;
  max-width: 16rem;
  height: 0.75rem;
}
</style>
