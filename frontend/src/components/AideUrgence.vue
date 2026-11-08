<script setup>
import { computed, ref, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePays } from '@/composables/usePays'
import NumeroAide from '@/components/NumeroAide.vue'
import PaysSelecteur from '@/components/PaysSelecteur.vue'

const { t } = useI18n()
const { pays, infos, nomPays } = usePays()

const idSelecteur = useId()
const ouvert = ref(false)
const autres = computed(() => infos.value?.autres ?? [])
</script>

<template>
  <div class="aide-urgence">
    <i18n-t keypath="aide.ecoute" tag="p" class="ligne">
      <template #ecoute><NumeroAide type="ecoute" details /></template>
    </i18n-t>

    <ul v-if="autres.length" class="autres">
      <li v-for="a in autres" :key="a.numero"><NumeroAide :contact="a" details /></li>
    </ul>

    <i18n-t keypath="aide.urgence" tag="p" class="ligne">
      <template #urgence><NumeroAide type="urgence" /></template>
    </i18n-t>

    <p class="ligne ligne-pays">
      <span>{{ t('aide.pour', { pays: nomPays(pays) }) }}</span>
      <button
        type="button"
        class="btn-text theme-inverse bouton-pays"
        :aria-expanded="String(ouvert)"
        :aria-controls="idSelecteur"
        @click="ouvert = !ouvert"
      >
        {{ t('aide.changer') }}
      </button>
    </p>
    <div v-show="ouvert" :id="idSelecteur">
      <PaysSelecteur />
    </div>
  </div>
</template>

<style scoped>
.aide-urgence {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.ligne {
  margin: 0;
}
.autres {
  margin: 0;
  padding-left: 1.25rem;
  font-size: 0.875rem;
}
.ligne-pays {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem 0.5rem;
  font-size: 0.875rem;
  color: color-mix(in srgb, currentColor 80%, transparent);
}
.bouton-pays {
  padding: 0.125rem 0.375rem;
  font-size: inherit;
  text-decoration: underline;
}
</style>
