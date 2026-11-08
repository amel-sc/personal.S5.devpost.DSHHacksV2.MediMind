<script setup>
import { computed, nextTick, onMounted, ref, useId, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const idTitre = useId()
const refTitre = ref(null)

// Adresse demandée, décodée pour être lisible (« /journée » au lieu de « /journ%C3%A9e »)
const adresse = computed(() => {
  try {
    return decodeURI(route.fullPath)
  } catch {
    return route.fullPath // encodage invalide : on garde la version brute
  }
})

// Vue Router enregistre la page précédente dans history.state.back.
// Si la valeur est null, on est arrivé directement ici (lien externe, adresse tapée…)
const peutRevenir = ref(false)

function miseEnPlace() {
  peutRevenir.value = Boolean(window.history.state?.back)
  refTitre.value?.focus()
}

onMounted(miseEnPlace)

// Même composant réutilisé de /abc vers /xyz : onMounted ne se relance pas
watch(
  () => route.fullPath,
  async () => {
    await nextTick()
    miseEnPlace()
  },
)
</script>

<template>
  <div class="vue-introuvable">
    <section class="etat-vide" :aria-labelledby="idTitre">
      <p class="emoji-vide" aria-hidden="true">🧭</p>

      <h1 :id="idTitre" ref="refTitre" tabindex="-1">{{ t('pages.introuvable') }}</h1>

      <p class="sans-marge">{{ t('notFound.texte') }}</p>

      <p class="adresse">
        <span class="texte-attenue">{{ t('notFound.adresse') }}</span>
        <code dir="ltr">{{ adresse }}</code>
      </p>

      <div class="etat-vide-actions">
        <RouterLink :to="{ name: 'conversation' }" class="btn-solid theme-primary btn-styled">
          {{ t('notFound.conversation') }}
        </RouterLink>
        <RouterLink :to="{ name: 'humeurList' }" class="btn-outline theme-primary btn-styled">
          {{ t('notFound.journal') }}
        </RouterLink>
        <button
          v-if="peutRevenir"
          type="button"
          class="btn-text theme-inverse bouton-icone"
          @click="router.back()"
        >
          <i class="bi bi-arrow-left" aria-hidden="true"></i>
          {{ t('notFound.retour') }}
        </button>
      </div>

      <i18n-t keypath="aide.besoin" tag="p" class="aide-urgence">
        <template #n3114><a href="tel:3114">3114</a></template>
      </i18n-t>
    </section>
  </div>
</template>

<style scoped>
.vue-introuvable {
  flex: 1 1 auto;
  overflow: auto;
  padding: 1.5rem 1rem;
}
.sans-marge {
  margin: 0;
}
.texte-attenue {
  color: color-mix(in srgb, currentColor 80%, transparent);
}
.emoji-vide {
  margin: 0;
  font-size: 3rem;
  line-height: 1;
}
.adresse {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: baseline;
  gap: 0.375rem;
  max-width: 100%;
  margin: 0;
  font-size: 0.875rem;
}
.adresse code {
  max-width: 100%;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  background: color-mix(in srgb, currentColor 10%, transparent);
  overflow-wrap: anywhere; /* une adresse très longue ne déborde pas */
}
.bouton-icone {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
.aide-urgence {
  margin: 0;
  font-size: 0.875rem;
}
</style>
