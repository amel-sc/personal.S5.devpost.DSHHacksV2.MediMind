export function dateHeure(texte) {
  const d = new Date(texte.replace(' ', 'T'))
  return d.toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })
}
// function to convert date to date local
export function dateLocale(dateUtc) {
  // SQLite renvoie souvent "YYYY-MM-DD HH:MM:SS", sans suffixe de fuseau.
  const iso = dateUtc.replace(' ', 'T') + 'Z'
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(new Date(iso))
}
