export function dateHeure(texte) {
  const d = new Date(texte.replace(' ', 'T'))
  return d.toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })
}