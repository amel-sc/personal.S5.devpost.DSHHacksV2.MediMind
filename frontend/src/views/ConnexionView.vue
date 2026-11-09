<script setup>
import { computed, ref, watchPostEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/services/api'
import { messageErreur } from '@/utils/erreur'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const email = ref('')
const motDePasse = ref('')
const afficherMotDePasse = ref(false)
const envoiEnCours = ref(false)
const erreur = ref(null)
const erreurChamp = ref({})

const peutEnvoyer = computed(
  () => email.value.trim() && motDePasse.value && !envoiEnCours.value,
)

watchPostEffect(() => {
  document.title = `${t('connexion.titre')} · MediMind`
})

async function connecter() {
  if (!peutEnvoyer.value) return

  erreur.value = null
  erreurChamp.value = {}
  envoiEnCours.value = true

  try {
    const data = {
      email: email.value.trim(),
      mot_de_passe: motDePasse.value,
    }

    // À adapter au nom de la méthode et au format réels de ton API.
    const resultat = await api.auth.connexion(data)
    console.log("Message : "+resultat.message)
    console.log("Data : "+ resultat.data == null ? '' : resultat.data)
    console.log("errors: "+ resultat.errors == null ? '' : resultat.errors)

    // // À adapter à la réponse du backend et au système d’authentification du projet.
    // if (resultat?.access_token) {
    //   localStorage.setItem('access_token', resultat.access_token)
    // }

    // const destination =
    //   typeof route.query.redirect === 'string' ? route.query.redirect : '/'

    // await router.replace(destination)
  } catch (e) {
    console.error(e)
    erreur.value = messageErreur(e)
    erreurChamp.value = e.errors
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <main class="page-connexion">
    <section class="carte-connexion card" aria-labelledby="titre-connexion">
      <div class="logo" aria-hidden="true">
        <i class="bi bi-chat-heart"></i>
      </div>

      <header class="entete">
        <h1 id="titre-connexion">{{ t('connexion.titre') }}</h1>
        <p>{{ t('connexion.sousTitre') }}</p>
      </header>

      <form class="formulaire" @submit.prevent="connecter">
        <div v-if="erreur" class="alert theme-danger" role="alert">
          {{ erreur }}
        </div>

        <div class="champ">
          <label for="email">{{ t('connexion.email') }}</label>
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
          <small
            v-if="erreurChamp.email"
            id="erreur-email"
            class="texte-invalide"
          >
            {{ t('connexion.erreurs.'+erreurChamp.email) }}
          </small>
        </div>

        <div class="champ">
          <label for="mot-de-passe">{{ t('connexion.motDePasse') }}</label>
          <input
            id="mot-de-passe"
            v-model="motDePasse"
            class="form-control"
            :type="afficherMotDePasse ? 'text' : 'password'"
            name="current-password"
            autocomplete="current-password"
            required
          />
          <small
            v-if="erreurChamp.mdp"
            id="erreur-email"
            class="texte-invalide"
          >
            {{ t('connexion.erreurs.'+erreurChamp.mdp) }}
          </small>
        </div>

        <label class="case-mot-de-passe">
          <input v-model="afficherMotDePasse" type="checkbox" />
          {{ t('connexion.afficherMotDePasse') }}
        </label>

        <button
          type="submit"
          class="btn-solid theme-primary btn-styled bouton-connexion"
          :disabled="!peutEnvoyer"
        >
          <span v-if="envoiEnCours" class="mm-spinner mm-spinner-sm" aria-hidden="true"></span>
          {{ envoiEnCours ? t('connexion.enCours') : t('connexion.bouton') }}
        </button>
      </form>

      <p class="lien-inscription">
        {{ t('connexion.pasDeCompte') }}
        <RouterLink :to="{ name: 'inscription' }">
          {{ t('connexion.creerCompte') }}
        </RouterLink>
      </p>
    </section>
  </main>
</template>

<style scoped>
.page-connexion {
  display: grid;
  place-items: center;
  min-height: 100%;
  overflow-y: auto;
  padding: 2rem 1rem;
}

.carte-connexion {
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

.bouton-connexion {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  min-height: 2.75rem;
  margin-top: 0.25rem;
}

.bouton-connexion:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.lien-inscription {
  margin: 1.5rem 0 0;
  text-align: center;
  font-size: 0.925rem;
}

.lien-inscription a {
  color: var(--mm-accent);
  font-weight: 600;
}

@media (max-width: 30rem) {
  .carte-connexion {
    padding: 1.5rem;
  }
}
</style>
