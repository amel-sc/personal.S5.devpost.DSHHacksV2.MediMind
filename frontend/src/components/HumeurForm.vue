<script setup>
import { computed, ref, useId } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { api } from '@/services/api'
import { messageErreur } from '@/utils/erreur'
import { niveauHumeur, estDifficile } from '@/utils/humeur'

const props = defineProps({
  humeurs: { type: Array, required: true },
  humeurCauses: { type: Array, required: true },
})

const NOTE_MAX = 500
const uid = useId()
const router = useRouter()
const formulaire = ref(null)

// Champs
const humeur = ref(null) // VALEUR de l'humeur (humeur.val : 1 = Très bien … 5 = Très mal)
const note = ref('')
const causes = ref([])   // ids de la table humeur_cause

// États
const envoi = ref(false)
const tentative = ref(false)
const enregistre = ref(false)
const erreur = ref(null)
const erreursChamps = ref({})

const humeurChoisie = computed(() => props.humeurs.find((h) => h.val === humeur.value) ?? null)
const afficherSoutien = computed(() => humeur.value !== null && estDifficile(humeur.value))
const modifie = computed(
  () => humeur.value !== null || note.value.trim() !== '' || causes.value.length > 0
)

// ApiError.errors peut contenir un texte ou une liste de textes par champ
function premierMessage(champ) {
  const m = erreursChamps.value?.[champ]
  return Array.isArray(m) ? m[0] : m ?? null
}

const erreurHumeur = computed(
  () =>
    premierMessage('id_humeur') ??
    (tentative.value && humeur.value === null
      ? "Choisissez l'humeur qui vous correspond le mieux."
      : null)
)
const erreurNote = computed(() => premierMessage('note'))
const erreurCauses = computed(() => premierMessage('id_humeur_causes'))

async function envoyer() {
  tentative.value = true
  erreur.value = null
  erreursChamps.value = {}

  if (humeur.value === null) {
    formulaire.value?.querySelector('input[type="radio"]')?.focus()
    return
  }

  envoi.value = true
  try {
    const response = await api.humeurJours.save({
      id_humeur: humeur.value, // le backend attend la valeur (humeur.val)
      note: note.value.trim(),
      id_humeur_causes: causes.value,
    })
    enregistre.value = true
    router.replace(`/humeur/${response.id_humeur_jours}`)
  } catch (e) {
    console.error(e)
    erreur.value = messageErreur(e)
    erreursChamps.value = e?.errors ?? {}
  } finally {
    envoi.value = false
  }
}

// Évite de perdre une saisie en cliquant ailleurs par erreur
onBeforeRouteLeave(() => {
  if (enregistre.value || !modifie.value) return true
  return window.confirm("Votre saisie n'est pas enregistrée. Quitter quand même ?")
})
</script>

<template>
  <form ref="formulaire" novalidate :aria-busy="envoi" @submit.prevent="envoyer">
    <div v-if="erreur" class="alert theme-danger mb-4" role="alert">{{ erreur }}</div>

    <!-- 1. Humeur -->
    <fieldset
      class="mb-4"
      :aria-describedby="erreurHumeur ? `${uid}-err-humeur` : undefined"
    >
      <legend class="h6 mb-2">
        Comment vous sentez-vous ?
        <span class="small fw-normal opacity-75">(obligatoire)</span>
      </legend>

      <div class="choix-humeur" :class="{ invalide: erreurHumeur }">
        <div v-for="o in humeurs" :key="o.id" class="option">
          <input
            :id="`${uid}-humeur-${o.val}`"
            v-model="humeur"
            class="input-cache"
            type="radio"
            :name="`${uid}-humeur`"
            :value="o.val"
          />
          <label :for="`${uid}-humeur-${o.val}`" class="carte-choix">
            <span class="emoji" aria-hidden="true">{{ niveauHumeur(o.val).emoji }}</span>
            <span class="small">{{ o.desce }}</span>
          </label>
        </div>
      </div>

      <p v-if="erreurHumeur" :id="`${uid}-err-humeur`" class="message-erreur small mt-2 mb-0">
        <i class="bi bi-exclamation-circle" aria-hidden="true"></i>
        {{ erreurHumeur }}
      </p>
    </fieldset>

    <!-- Soutien si "Mal" ou "Très mal" (zone toujours présente pour être annoncée) -->
    <div aria-live="polite">
      <aside v-if="afficherSoutien" class="alert theme-info mb-4" aria-label="Soutien">
        <p class="mb-2">
          Merci de l'avoir noté, ce n'est pas toujours facile.
          Si vous en ressentez le besoin, vous pouvez en parler :
        </p>
        <ul class="mb-0">
          <li><RouterLink :to="{ name: 'conversation' }">avec MediMind</RouterLink>, à tout moment ;</li>
          <li>au <a href="tel:3114">3114</a> (gratuit, 24h/24) si vous vous sentez en détresse.</li>
        </ul>
      </aside>
    </div>

    <!-- 2. Note -->
    <div class="champ mb-4">
      <label :for="`${uid}-note`" class="h6 mb-0">
        Quelques mots sur votre journée
        <span class="small fw-normal opacity-75">(facultatif)</span>
      </label>
      <textarea
        :id="`${uid}-note`"
        v-model="note"
        class="form-control"
        rows="4"
        :maxlength="NOTE_MAX"
        placeholder="Ex. : J'ai bien dormi, mais l'examen de demain me stresse un peu."
        :aria-invalid="erreurNote ? 'true' : undefined"
        :aria-describedby="[`${uid}-note-aide`, erreurNote && `${uid}-err-note`].filter(Boolean).join(' ')"
      ></textarea>
      <p :id="`${uid}-note-aide`" class="small opacity-75 mb-0 text-end">
        {{ note.length }} / {{ NOTE_MAX }} caractères
      </p>
      <p v-if="erreurNote" :id="`${uid}-err-note`" class="message-erreur small mb-0">
        {{ erreurNote }}
      </p>
    </div>

    <!-- 3. Causes (on envoie bien l'id ici) -->
    <fieldset class="mb-4" :aria-describedby="`${uid}-aide-causes`">
      <legend class="h6 mb-1">
        Qu'est-ce qui influence votre humeur ?
        <span class="small fw-normal opacity-75">(facultatif)</span>
      </legend>
      <p :id="`${uid}-aide-causes`" class="small opacity-75 mb-2">Plusieurs choix possibles.</p>

      <div class="choix-causes">
        <div v-for="c in humeurCauses" :key="c.id" class="option">
          <input
            :id="`${uid}-cause-${c.id}`"
            v-model="causes"
            class="input-cache"
            type="checkbox"
            :value="c.id"
          />
          <label :for="`${uid}-cause-${c.id}`" class="puce">
            <i class="bi bi-check-lg icone-check" aria-hidden="true"></i>
            {{ c.desce ?? c.val }}
          </label>
        </div>
      </div>

      <p v-if="erreurCauses" class="message-erreur small mt-2 mb-0">{{ erreurCauses }}</p>
    </fieldset>

    <!-- Actions -->
    <div class="actions">
      <RouterLink to="/humeur/list" class="btn-text theme-inverse">Annuler</RouterLink>
      <button type="submit" class="btn-solid theme-primary btn-styled" :disabled="envoi">
        <span v-if="envoi" class="spinner-border spinner-sm" aria-hidden="true"></span>
        {{ envoi ? 'Enregistrement…' : 'Enregistrer mon humeur' }}
      </button>
    </div>
  </form>
</template>
