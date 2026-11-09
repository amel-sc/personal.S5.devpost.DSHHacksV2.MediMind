import { i18n } from '../i18n'
import { dateLocale } from './format'

export const ECHELLE = [1, 2, 3, 4, 5] // 1 = Très bien … 5 = Très mal

// Couleurs douces : pas de rouge "danger" pour une humeur basse
const NIVEAUX = {
  1: { emoji: '😄', theme: 'theme-success' },
  2: { emoji: '🙂', theme: 'theme-success' },
  3: { emoji: '😐', theme: 'theme-warning' },
  4: { emoji: '😕', theme: 'theme-info' },
  5: { emoji: '😢', theme: 'theme-info' },
}
const PAR_DEFAUT = { emoji: '📝', theme: 'theme-secondary' }

/**
 * Libellé traduit d'une humeur.
 * Ordre : traduction du niveau → texte venant de la base → « Non renseignée ».
 */
export function libelleHumeur(humeur) {
  const { t, te } = i18n.global
  const cle = `humeur.niveaux.${Number(humeur?.humeur_val)}`
  if (te(cle)) return t(cle)
  return humeur?.humeur_desce || t('journal.nonRenseignee')
}

/**
 * Libellé traduit d'une cause.
 * Ordre : traduction du code (colonne `code`, à venir) → texte venant de la base → valeur brute.
 */
export function libelleCause(cause) {
  const { t, te } = i18n.global
  const cle = cause?.code ? `humeur.causes.${cause.code}` : null
  if (cle && te(cle)) return t(cle)
  return cause?.cause_desce || String(cause?.cause_val ?? '') || t('journal.nonRenseignee')
}

export function niveauHumeur(val) {
  return NIVEAUX[Number(val)] ?? PAR_DEFAUT
}

export function estDifficile(val) {
  return Number(val) >= 4 // "Mal" ou "Très mal"
}

export function estActive(h) {
  // status_val peut être null à cause du LEFT JOIN : on considère alors l'entrée active
  return h?.status_val == null || Number(h.status_val) === 1
}

// SQLite renvoie souvent "2026-11-07 10:00:00" : Safari ne sait pas lire l'espace
export function versDate(valeur) {
  if (!valeur) return null
  const d = new Date(String(valeur).replace(' ', 'T') + 'Z')
  return Number.isNaN(d.getTime()) ? null : d
}

