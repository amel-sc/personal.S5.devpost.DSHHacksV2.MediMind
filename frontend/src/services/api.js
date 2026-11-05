const BASE = '/api'

/** Erreur renvoyée par l'API : message général + erreurs par champ. */
export class ApiError extends Error {
  constructor(status, corps) {
    super(corps?.message ?? `Erreur ${status}`)
    this.status = status
    this.errors = corps?.errors ?? {}
  }
}

async function requete(methode, chemin, donnees) {
   const estFormData = donnees instanceof FormData

  const options = {
    method: methode,
    headers: { 
      Accept: 'application/json' 
    },
  }
  if (donnees !== undefined) {
    if (estFormData) {
      // Ne pas définir Content-Type manuellement :
      // fetch ajoutera le boundary multipart.
      options.body = donnees
    } else {
      options.headers['Content-Type'] = 'application/json'
      options.body = JSON.stringify(donnees)
    }
  }

  const reponse = await fetch(BASE + chemin, options)
  const corps = await reponse.json().catch(() => null)

  if (!reponse.ok) {
    throw new ApiError(reponse.status, corps)
  }
  return corps
}

// function to get all messages by conversatino
export function getMessages(id) {
  return requete('GET', `/messages?id_conversation=${id}`,)
}

// function to get all conversation
export function getConversations() {
  return requete('GET', '/conversation')
}

// function to get response of message
export function traitementMessage(donnees) {
  return requete('POST', '/message/traitement', donnees) 
}

// function to send message to medimind
export function sendMessage(donnees) {
  return requete('POST', '/message', donnees)
}