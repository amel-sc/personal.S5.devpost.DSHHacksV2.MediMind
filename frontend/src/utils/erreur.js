import { ApiError } from '@/services/api'

export function messageErreur(e) {
  if (e instanceof ApiError) {
    if (e.status >= 500) return 'Le serveur rencontre un problème. Réessayez dans un instant.'
    if (e.status === 422) return 'Certaines informations ne sont pas valides. Vérifiez le formulaire.'
    return e.message
  }
  return 'Impossible de joindre le serveur. Vérifiez votre connexion.'
}