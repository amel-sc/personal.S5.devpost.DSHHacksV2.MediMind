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

export const api = {
  message: {
    lister: (id) => requete('GET', `/message?id_conversation=${id}`),
    traitement: (donnees) => requete('POST', '/message/traitement', donnees),
    send: (donnees) => requete('POST', '/message', donnees)
  },
  conversation: {
    lister: () => requete('GET', '/conversation')
  }
}