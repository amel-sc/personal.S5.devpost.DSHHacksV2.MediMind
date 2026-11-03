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

// // function to to prediction
// export function prediction(donnees) {
//   return requete ('POST', `/prediction`, donnees)
// }

// // function to get prediction by id
// export function getPrediction(id) {
//     return requete('GET', `/prediction/${id}`)
// }