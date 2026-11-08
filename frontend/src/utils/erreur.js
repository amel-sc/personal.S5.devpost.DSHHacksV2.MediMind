import { i18n } from '@/i18n'
import { ApiError } from '@/services/api'

export function messageErreur(e) {
  const { t, te } = i18n.global

  if (e instanceof ApiError) {
    // 1. Code connu renvoyé par le backend → traduction
    if (e.code && te(`erreurs.codes.${e.code}`)) return t(`erreurs.codes.${e.code}`)
    if (e.status >= 500) return t('erreurs.serveur')
    if (e.status === 422) return t('erreurs.validation')
    // 2. Sinon, le message du serveur (en français) vaut mieux que rien
    return e.message || t('erreurs.inconnue')
  }
  if (e instanceof TypeError) return t('erreurs.reseau') // fetch hors ligne
  return t('erreurs.inconnue')
}
