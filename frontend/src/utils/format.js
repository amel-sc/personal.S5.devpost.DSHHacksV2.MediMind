export function dateHeure(texte) {
  const d = new Date(texte.replace(' ', 'T'))
  return d.toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })
}
// function to convert date to date local
function dateLocale(dateUtc) {
  // SQLite renvoie souvent "YYYY-MM-DD HH:MM:SS", sans suffixe de fuseau.
  const iso = dateUtc.replace(' ', 'T') + 'Z'
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(iso))
}
