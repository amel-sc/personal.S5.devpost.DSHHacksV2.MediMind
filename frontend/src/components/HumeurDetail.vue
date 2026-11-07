<script setup>
import { computed, useId } from 'vue'
import { ECHELLE, niveauHumeur } from '@/utils/humeur'

const props = defineProps({
  humeurJours: { type: Object, default: null },
  humeurJoursCauses: { type: Array, default: () => [] },
  titre: { type: String, default: "Votre humeur aujourd'hui" },
})

const idTitre = useId()
const valeur = computed(() => Number(props.humeurJours?.humeur_val))
const niveau = computed(() => niveauHumeur(valeur.value))
const causes = computed(() => props.humeurJoursCauses ?? [])
const note = computed(() => String(props.humeurJours?.note ?? '').trim())
</script>

<template>
  <article
    v-if="humeurJours"
    class="card card-subtle"
    :class="niveau.theme"
    :aria-labelledby="idTitre"
  >
    <div class="card-body">
      <h2 :id="idTitre" class="h5 mb-3">{{ titre }}</h2>

      <div class="d-flex align-items-center gap-3 mb-3">
        <span class="emoji-humeur" aria-hidden="true">{{ niveau.emoji }}</span>
        <div>
          <p class="fs-5 fw-semibold mb-1">
            {{ humeurJours.humeur_desce ?? 'Humeur non renseignée' }}
          </p>
          <!-- Échelle visuelle seulement : le texte ci-dessus suffit aux lecteurs d'écran -->
          <ol class="echelle list-unstyled d-flex gap-1 mb-0" aria-hidden="true">
            <li v-for="v in ECHELLE" :key="v" :class="{ actif: v === valeur }">
              {{ niveauHumeur(v).emoji }}
            </li>
          </ol>
        </div>
      </div>

      <template v-if="note">
        <h3 class="h6 mb-1">Votre note</h3>
        <p class="note mb-3">{{ note }}</p>
      </template>

      <h3 class="h6 mb-2">Ce qui a influencé votre humeur</h3>
      <ul v-if="causes.length" class="list-unstyled d-flex flex-wrap gap-2 mb-0">
        <li v-for="cause in causes" :key="cause.id">
          <span class="badge badge-subtle theme-secondary">
            {{ cause.cause_desce ?? cause.cause_val }}
          </span>
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
.echelle li {
  font-size: 1.1rem;
  opacity: 0.35;
  filter: grayscale(1);
}
.echelle li.actif {
  opacity: 1;
  filter: none;
  transform: scale(1.2);
}
.note {
  white-space: pre-line; /* conserve les retours à la ligne */
}
</style>
