<script setup>
import { useI18n } from 'vue-i18n'
import { LANGUES, changerLangue } from '@/i18n'

const { locale, t } = useI18n()
</script>

<template>
  <div class="langue-selecteur">
    <label for="choix-langue" class="visually-hidden">{{ t('langue.choisir') }}</label>
    <i class="bi bi-translate" aria-hidden="true"></i>
    <select
      id="choix-langue"
      class="form-control choix"
      :value="locale"
      @change="changerLangue($event.target.value)"
    >
      <!-- lang : chaque nom de langue est lu avec sa propre prononciation -->
      <option v-for="l in LANGUES" :key="l.code" :value="l.code" :lang="l.code">
        {{ l.nom }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.langue-selecteur {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.choix {
  inline-size: auto;
}
</style>
