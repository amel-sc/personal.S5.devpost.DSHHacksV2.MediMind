import { computed, shallowReactive } from 'vue'

// État au niveau du module : il survit à la destruction de ConversationView
const enCours = shallowReactive(new Map()) // id_conversation → Promise<réponse>
const nonLues = shallowReactive(new Set()) // conversations avec une réponse pas encore vue

/**
 * Lance la demande de réponse pour une conversation (une seule à la fois par conversation).
 * Renvoie la promesse, que plusieurs vues peuvent suivre.
 */
export function demanderReponse(idConversation, requete) {
  if (enCours.has(idConversation)) return enCours.get(idConversation)

  const promesse = requete()
    .then((reponse) => {
      nonLues.add(idConversation) // la vue la retire si l'utilisateur regarde cette conversation
      return reponse
    })
    .finally(() => enCours.delete(idConversation))

  enCours.set(idConversation, promesse)
  return promesse
}

export const reponseEnCours = (id) => enCours.has(id)
export const promesseReponse = (id) => enCours.get(id)
export const estNonLue = (id) => nonLues.has(id)
export const marquerLue = (id) => nonLues.delete(id)
export const nombreNonLues = computed(() => nonLues.size)
