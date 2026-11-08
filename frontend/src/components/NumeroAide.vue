<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePays } from '@/composables/usePays'

// Plusieurs nœuds racines (texte + liens) : on ne laisse pas Vue y coller les attributs
defineOptions({ inheritAttrs: false })

const props = defineProps({
  type: { type: String, default: 'ecoute', validator: (v) => ['ecoute', 'urgence'].includes(v) },
  // Contact précis à afficher (lignes « autres ») ; sinon la ligne principale du pays
  contact: { type: Object, default: null },
  // Ajoute « (nom, gratuit, 24 h/24) »
  details: { type: Boolean, default: false },
})

const { t, locale } = useI18n()
const { infos, lienAnnuaire } = usePays()

const lienTel = (numero) => `tel:${numero.replace(/[^\d+]/g, '')}`

function localise(valeur) {
  if (!valeur || typeof valeur === 'string') return valeur ?? ''
  return valeur[locale.value] ?? valeur.fr ?? Object.values(valeur)[0] ?? ''
}

function nomLangue(code) {
  try {
    return new Intl.DisplayNames([locale.value], { type: 'language' }).of(code) ?? code
  } catch {
    return code
  }
}

/* ---------- Ligne d'écoute ---------- */
const ecoute = computed(() => props.contact ?? infos.value?.ecoute ?? null)

const texteDetails = computed(() => {
  const e = ecoute.value
  if (!e) return ''
  const morceaux = []
  const nom = localise(e.nom)
  if (nom && nom !== e.numero) morceaux.push(nom)
  if (e.public) morceaux.push(t(`urgences.public.${e.public}`))
  if (e.langue) morceaux.push(t('urgences.langue', { langue: nomLangue(e.langue) }))
  if (e.gratuit) morceaux.push(t('urgences.gratuit'))
  if (e.h24) morceaux.push(t('urgences.h24'))
  return morceaux.join(', ')
})

/* ---------- Urgence : « 15 ou 112 » / « 15 or 112 », chaque numéro cliquable ---------- */
const partiesUrgence = computed(() => {
  const numeros = infos.value?.urgence ?? []
  if (!numeros.length) return []
  try {
    return new Intl.ListFormat(locale.value, { type: 'disjunction' })
      .formatToParts(numeros)
      .map((p) => ({ lien: p.type === 'element', texte: p.value }))
  } catch {
    return numeros.flatMap((n, i) => [
      ...(i ? [{ lien: false, texte: ' / ' }] : []),
      { lien: true, texte: n },
    ])
  }
})
</script>

<template>
  <!-- Urgence vitale -->
  <template v-if="type === 'urgence'">
    <template v-if="partiesUrgence.length">
      <template v-for="(p, i) in partiesUrgence" :key="i">
        <a v-if="p.lien" :href="lienTel(p.texte)" class="numero" dir="ltr">{{ p.texte }}</a>
        <template v-else>{{ p.texte }}</template>
      </template>
    </template>
    <template v-else>{{ t('urgences.urgenceLocale') }}</template>
  </template>

  <!-- Ligne d'écoute connue -->
  <template v-else-if="ecoute">
    <a :href="lienTel(ecoute.numero)" class="numero" dir="ltr">{{ ecoute.numero }}</a>
    <template v-if="details && texteDetails"> ({{ texteDetails }})</template>
  </template>

  <!-- Pays sans liste vérifiée : annuaire international -->
  <a v-else :href="lienAnnuaire" target="_blank" rel="noopener noreferrer">
    {{ t('urgences.annuaire') }}<span class="masque-visuellement"> {{ t('urgences.nouvelOnglet') }}</span>
  </a>
</template>

<style scoped>
.numero {
  font-weight: 600;
  white-space: nowrap; /* « 0800 32 123 » ne se coupe pas en fin de ligne */
}
</style>
