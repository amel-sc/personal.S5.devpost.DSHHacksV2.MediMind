<script setup>
import { useId } from 'vue'
import { useTheme } from '@/composables/useTheme'

const { theme } = useTheme()
const uid = useId()

const options = [
  { valeur: 'auto', label: 'Automatique', icone: 'bi-circle-half' },
  { valeur: 'light', label: 'Clair', icone: 'bi-sun' },
  { valeur: 'dark', label: 'Sombre', icone: 'bi-moon-stars' },
]
</script>

<template>
  <fieldset class="selecteur-theme">
    <legend class="visually-hidden">Thème</legend>
    <div v-for="o in options" :key="o.valeur" class="option">
      <input
        :id="`${uid}-${o.valeur}`"
        v-model="theme"
        class="input-cache"
        type="radio"
        :name="`${uid}-theme`"
        :value="o.valeur"
      />
      <label :for="`${uid}-${o.valeur}`" :title="o.label">
        <i class="bi" :class="o.icone" aria-hidden="true"></i>
        <span class="visually-hidden">{{ o.label }}</span>
      </label>
    </div>
  </fieldset>
</template>

<style scoped>
.selecteur-theme {
  display: inline-flex;
  gap: 0.125rem;
  padding: 0.125rem;
  margin: 0;
  border: 1px solid rgba(127, 127, 127, 0.35);
  border-radius: 999px;
}
.option {
  position: relative;
}
.input-cache {
  position: absolute;
  opacity: 0;
  width: 1px;
  height: 1px;
  margin: 0;
  pointer-events: none;
}
label {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 999px;
  cursor: pointer;
  opacity: 0.65;
}
label:hover {
  opacity: 1;
  background-color: rgba(127, 127, 127, 0.1);
}
input:checked + label {
  opacity: 1;
  background-color: rgba(127, 127, 127, 0.25);
}
input:focus-visible + label {
  outline: 3px solid currentColor;
  outline-offset: 2px;
}
</style>
