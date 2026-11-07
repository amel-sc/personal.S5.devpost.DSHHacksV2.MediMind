// Adapte à l'échelle utilisée par ton backend (5, 10...)
export const NOTE_MAX = 5

// Couleurs volontairement douces : pas de rouge "danger" pour une humeur basse
export function niveauNote(note) {
  if (typeof note !== 'number') return null
  const ratio = note / NOTE_MAX
  if (ratio < 0.4) return { theme: 'theme-info', label: 'Difficile', emoji: '😔' }
  if (ratio < 0.7) return { theme: 'theme-warning', label: 'Mitigée', emoji: '😐' }
  return { theme: 'theme-success', label: 'Bonne', emoji: '🙂' }
}
