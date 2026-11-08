import { createI18n } from 'vue-i18n'
import fr from './fr'
import en from './en'

export const LANGUES = [
  { code: 'fr', nom: 'Français' },
  { code: 'en', nom: 'English' },
]
export const CLE_LANGUE = 'medimind-langue'

function langueInitiale() {
  const enregistree = localStorage.getItem(CLE_LANGUE)
  if (LANGUES.some((l) => l.code === enregistree)) return enregistree
  // Sinon la langue du navigateur, et le français par défaut
  return navigator.language?.toLowerCase().startsWith('en') ? 'en' : 'fr'
}

export const i18n = createI18n({
  legacy: false, // API Composition (useI18n)
  locale: langueInitiale(),
  fallbackLocale: 'fr', // une clé manquante en anglais s'affiche en français
  messages: { fr, en },
})

export function changerLangue(code) {
  i18n.global.locale.value = code
  localStorage.setItem(CLE_LANGUE, code)
  document.documentElement.lang = code
}

// <html lang="…"> correct dès le démarrage
document.documentElement.lang = i18n.global.locale.value
