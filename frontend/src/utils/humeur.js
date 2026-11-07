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
  const d = new Date(String(valeur).replace(' ', 'T'))
  return Number.isNaN(d.getTime()) ? null : d
}
