import { computed, ref } from 'vue'
import { i18n } from '@/i18n'
import { URGENCES, PAYS_PAR_DEFAUT, FUSEAUX } from '@/data/urgences'

const CLE_PAYS = 'medimind-pays'
export const AUTRE = 'AUTRE' // « Autre pays » : on renvoie vers l'annuaire international
export const PAYS_DISPONIBLES = Object.keys(URGENCES)

const estCodePays = (v) => typeof v === 'string' && /^[A-Z]{2}$/.test(v)

/* Rien n'est envoyé à un serveur : tout se fait dans le navigateur */
function detecterPays() {
  // 1. Fuseau horaire (le plus fiable : un Belge a souvent un navigateur en « fr » sans région)
  try {
    const fuseau = Intl.DateTimeFormat().resolvedOptions().timeZone
    if (FUSEAUX[fuseau]) return FUSEAUX[fuseau]
  } catch { /* Intl indisponible */ }

  // 2. Région écrite dans les langues du navigateur : « fr-BE » → BE ; « fr » seul → rien
  //    (pas de maximize() : il transformerait « en » en « US », ce qui serait souvent faux)
  const langues = navigator.languages?.length ? navigator.languages : [navigator.language]
  for (const l of langues) {
    try {
      const region = new Intl.Locale(l).region
      if (estCodePays(region)) return region
    } catch { /* code de langue invalide */ }
  }

  // 3. Public principal de MediMind
  return PAYS_PAR_DEFAUT
}

function lireChoix() {
  try {
    const v = localStorage.getItem(CLE_PAYS)
    return estCodePays(v) || v === AUTRE ? v : null
  } catch {
    return null
  }
}

/* État partagé par toute l'app (créé une seule fois) */
const paysDetecte = detecterPays()
const choix = ref(lireChoix()) // null = automatique

const pays = computed(() => choix.value ?? paysDetecte)
const infos = computed(() => URGENCES[pays.value] ?? null)

const lienAnnuaire = computed(() => {
  const prefixe = i18n.global.locale.value === 'fr' ? '/fr-FR' : ''
  const chemin = estCodePays(pays.value) ? `/countries/${pays.value.toLowerCase()}` : ''
  return `https://findahelpline.com${prefixe}${chemin}`
})

/* Nom du pays dans la langue de l'interface, sans traduction à maintenir */
export function nomPays(code) {
  const { t, locale } = i18n.global
  if (!estCodePays(code)) return t('pays.autre')
  try {
    return new Intl.DisplayNames([locale.value], { type: 'region' }).of(code) ?? code
  } catch {
    return code
  }
}

export function changerPays(code) {
  choix.value = code || null
  try {
    if (choix.value) localStorage.setItem(CLE_PAYS, choix.value)
    else localStorage.removeItem(CLE_PAYS)
  } catch { /* stockage indisponible : le choix vaut pour cette session */ }
}

export function usePays() {
  return { pays, choix, paysDetecte, infos, lienAnnuaire, nomPays, changerPays }
}
