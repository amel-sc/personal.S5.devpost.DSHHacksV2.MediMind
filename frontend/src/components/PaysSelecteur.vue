<script setup>
import { computed, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePays, PAYS_DISPONIBLES, AUTRE } from '@/composables/usePays'

const { t, locale } = useI18n()
const { choix, paysDetecte, nomPays, changerPays } = usePays()
const id = useId()

const valeur = computed({
  get: () => choix.value ?? 'auto',
  set: (v) => changerPays(v === 'auto' ? null : v),
})

// Triés selon la langue de l'interface (« Belgique, Canada… » / « Belgium, Canada… »)
const options = computed(() =>
  PAYS_DISPONIBLES
    .map((code) => ({ code, nom: nomPays(code) }))
    .sort((a, b) => a.nom.localeCompare(b.nom, locale.value)),
)
</script>

<template>
  <div class="selecteur-pays">
    <label :for="id" class="label-pays">{{ t('pays.label') }}</label>
    <select :id="id" v-model="valeur" class="form-control" :aria-describedby="`${id}-aide`">
      <option value="auto">{{ t('pays.auto', { pays: nomPays(paysDetecte) }) }}</option>
      <option v-for="o in options" :key="o.code" :value="o.code">{{ o.nom }}</option>
      <option :value="AUTRE">{{ t('pays.autre') }}</option>
    </select>
    <p :id="`${id}-aide`" class="aide-pays">{{ t('pays.aide') }}</p>
  </div>
</template>

<style scoped>
.selecteur-pays {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.label-pays {
  font-size: 0.875rem;
  font-weight: 600;
}
.aide-pays {
  margin: 0;
  font-size: 0.8125rem;
  color: color-mix(in srgb, currentColor 75%, transparent);
}
</style>
