import { ref, watch } from 'vue'

const CLE = 'medimind-theme'
const THEMES = ['auto', 'light', 'dark']

function lire() {
  try {
    const v = localStorage.getItem(CLE)
    return THEMES.includes(v) ? v : 'auto'
  } catch {
    return 'auto' // navigation privée, stockage bloqué…
  }
}

function appliquer(theme) {
  const html = document.documentElement
  if (theme === 'auto') html.removeAttribute('data-bs-theme') // suit le système
  else html.setAttribute('data-bs-theme', theme)
}

// État partagé par toute l'application (créé une seule fois)
const theme = ref(lire())

watch(
  theme,
  (v) => {
    appliquer(v)
    try {
      if (v === 'auto') localStorage.removeItem(CLE)
      else localStorage.setItem(CLE, v)
    } catch { /* tant pis : le choix ne sera pas mémorisé */ }
  },
  { immediate: true }
)

export function useTheme() {
  return { theme }
}
