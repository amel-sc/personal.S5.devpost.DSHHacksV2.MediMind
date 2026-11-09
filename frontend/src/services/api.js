const BASE = '/api'

/** Erreur renvoyée par l'API : message général + erreurs par champ. */
export class ApiError extends Error {
  constructor(status, corps) {
    super(corps?.message ?? `Erreur ${status}`)
    this.status = status
    this.errors = corps?.errors ?? {}
    this.code = corps?.code ?? null
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
  },
  humeur: {
    lister: () => requete('GET', '/humeur')
  },
  humeurCause: {
    lister: () => requete('GET', '/humeur/cause')
  }, 
  humeurJours: {
    save: (donnees) => requete('POST', '/humeur/jours', donnees),
    lister: () => requete('GET', '/humeur/jours'),
    find: (id) => requete('GET', `/humeur/jours/${id}`),
    today: () => requete('GET', '/humeur/jours/today')
  },
  auth: {
    inscription: (donnees) => requete('POST', '/inscription', donnees),
    connexion: (donnees) => requete('POST', '/connexion', donnees)
  }
}