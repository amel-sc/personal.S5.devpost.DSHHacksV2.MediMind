<script setup>
import { computed, ref, watchPostEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'
import { messageErreur } from '@/utils/erreur'

const { t } = useI18n()
const router = useRouter()

const prenom = ref('')
const nom = ref('')
const email = ref('')
const dateNaissance = ref('')
const motDePasse = ref('')
const confirmation = ref('')
const envoiEnCours = ref(false)
const inscriptionReussie = ref(false)
const erreur = ref(null)
const erreurChamp = ref(null)
const afficherMotDePasse = ref(false)

const dateAujourdhui = new Date().toISOString().slice(0, 10)

const erreurConfirmation = computed(() => {
  if (!confirmation.value) return ''
  return confirmation.value === motDePasse.value
    ? ''
    : t('inscription.erreurs.confirmation')
})

const peutEnvoyer = computed(
  () =>
    nom.value.trim() &&
    prenom.value.trim() &&
    email.value.trim() &&
    dateNaissance.value &&
    motDePasse.value &&
    confirmation.value &&
    !erreurConfirmation.value &&
    !envoiEnCours.value,
)

watchPostEffect(() => {
  document.title = `${t('inscription.titre')} · MediMind`
})

async function inscrire() {
  erreur.value = null

  if (confirmation.value !== motDePasse.value) return
  if (!peutEnvoyer.value) return

  envoiEnCours.value = true

  try {
    // data
    const data = {
      first_name: prenom.value.trim(),
      last_name: nom.value.trim(),
      email: email.value.trim(),
      mdp: motDePasse.value,
      date_naissance: dateNaissance.value
    }

    await api.auth.inscription(data)

    inscriptionReussie.value = true
  } catch (e) {
    console.error(e)
    erreur.value = messageErreur(e)
    erreurChamp = e.errors
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <main class="page-inscription">
    <section class="carte-inscription card" aria-labelledby="titre-inscription">
      <div class="logo" aria-hidden="true">
        <i class="bi bi-chat-heart"></i>
      </div>

      <header class="entete">
        <h1 id="titre-inscription">{{ t('inscription.titre') }}</h1>
        <p>{{ t('inscription.sousTitre') }}</p>
      </header>

      <div
        v-if="inscriptionReussie"
        class="alert theme-success"
        role="status"
      >
        {{ t('inscription.succes') }}
      </div>

      <form v-else class="formulaire" @submit.prevent="inscrire">
        <div v-if="erreur" class="alert theme-danger" role="alert">
          {{ erreur }}
        </div>

        <div class="champ">
          <label for="prenom">{{ t('inscription.prenom') }}</label>
          <input
            id="prenom"
            v-model.trim="prenom"
            class="form-control"
            name="given-name"
            autocomplete="given-name"
            required
          />
        </div>

        <div class="champ">
          <label for="nom">{{ t('inscription.nom') }}</label>
          <input
            id="nom"
            v-model.trim="nom"
            class="form-control"
            name="given-name"
            autocomplete="given-name"
            required
          />
        </div>

        <div class="champ">
          <label for="email">{{ t('inscription.email') }}</label>
          <input
            id="email"
            v-model.trim="email"
            class="form-control"
            type="email"
            name="email"
            autocomplete="email"
            required
            maxlength="254"
          />
        </div>

        <div class="champ">
          <label for="date-naissance">{{ t('inscription.dateNaissance') }}</label>
          <input
            id="date-naissance"
            v-model="dateNaissance"
            class="form-control"
            type="date"
            name="date_naissance"
            aria-label="Date picker"
            autocomplete="bday"
            :max="dateAujourdhui"
            required
          />
        </div>


        <div class="champ">
          <label for="mot-de-passe">{{ t('inscription.motDePasse') }}</label>
          <input
            id="mot-de-passe"
            v-model="motDePasse"
            class="form-control"
            :type="afficherMotDePasse ? 'text' : 'password'"
            name="new-password"
            autocomplete="new-password"
            required
          />
        </div>

        <div class="champ">
          <label for="confirmation">{{ t('inscription.confirmation') }}</label>
          <input
            id="confirmation"
            v-model="confirmation"
            class="form-control"
            :class="{ invalide: erreurConfirmation }"
            :type="afficherMotDePasse ? 'text' : 'password'"
            name="confirm-password"
            autocomplete="new-password"
            required
            :aria-invalid="Boolean(erreurConfirmation)"
            :aria-describedby="erreurConfirmation ? 'erreur-confirmation' : undefined"
          />
          <small
            v-if="erreurConfirmation"
            id="erreur-confirmation"
            class="texte-invalide"
          >
            {{ erreurConfirmation }}
          </small>
        </div>

        <label class="case-mot-de-passe">
          <input v-model="afficherMotDePasse" type="checkbox" />
          {{ t('inscription.afficherMotDePasse') }}
        </label>

        <button
          type="submit"
          class="btn-solid theme-primary btn-styled bouton-inscription"
          :disabled="!peutEnvoyer"
        >
          <span v-if="envoiEnCours" class="mm-spinner mm-spinner-sm" aria-hidden="true"></span>
          {{ envoiEnCours ? t('inscription.enCours') : t('inscription.bouton') }}
        </button>
      </form>

      <p v-if="!inscriptionReussie" class="lien-connexion">
        {{ t('inscription.dejaCompte') }}
        <RouterLink to="/connexion">
          {{ t('inscription.seConnecter') }}
        </RouterLink>
      </p>
    </section>
  </main>
</template>

<style scoped>
.page-inscription {
  display: grid;
  place-items: center;
  min-height: 100%;
  overflow-y: auto;
  padding: 2rem 1rem;
}

.carte-inscription {
  width: min(100%, 29rem);
  padding: 2rem;
  border: 1px solid var(--mm-bordure);
  border-radius: 1rem;
  background-color: var(--mm-surface);
  box-shadow: 0 0.5rem 2rem rgb(0 0 0 / 6%);
}

.logo {
  display: grid;
  place-items: center;
  width: 3.5rem;
  height: 3.5rem;
  margin: 0 auto 1rem;
  border-radius: 1rem;
  color: var(--mm-accent);
  background-color: color-mix(in srgb, var(--mm-accent) 15%, transparent);
  font-size: 1.75rem;
}

.entete {
  margin-bottom: 1.5rem;
  text-align: center;
}

.entete h1 {
  margin: 0 0 0.35rem;
  font-size: 1.6rem;
}

.entete p {
  margin: 0;
  opacity: 0.75;
}

.formulaire {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.champ {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.champ label {
  font-size: 0.925rem;
  font-weight: 600;
}

.champ .form-control {
  width: 100%;
}

.aide-champ {
  opacity: 0.75;
}

.invalide {
  border-color: #dc3545;
}

.texte-invalide {
  color: #dc3545;
}

.case-mot-de-passe {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
}

.case-mot-de-passe input {
  width: 1.125rem;
  height: 1.125rem;
  accent-color: var(--mm-accent);
}

.bouton-inscription {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  min-height: 2.75rem;
  margin-top: 0.25rem;
}

.bouton-inscription:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.lien-connexion {
  margin: 1.5rem 0 0;
  text-align: center;
  font-size: 0.925rem;
}

.lien-connexion a {
  color: var(--mm-accent);
  font-weight: 600;
}

@media (max-width: 30rem) {
  .carte-inscription {
    padding: 1.5rem;
  }
}
</style>
