/*
 * Numéros d'aide par pays.
 * ⚠️ À revérifier au moins une fois par an (les numéros changent : le 988 canadien date de 2023).
 * Sources : sites officiels de chaque ligne + findahelpline.com.
 * N'indique « gratuit » ou « h24 » que si c'est confirmé par la ligne elle-même.
 */
export const VERIFIE_LE = '2026-11'
export const PAYS_PAR_DEFAUT = 'FR'

/*
 * Pour chaque pays :
 *  - ecoute : ligne principale (prévention du suicide / détresse)
 *  - autres : lignes complémentaires (facultatif)
 *  - urgence : numéros d'urgence vitale, dans l'ordre conseillé
 * `nom` : nom propre du service (pas traduit), ou { fr, en } si le service a un nom dans chaque langue.
 * `langue` : code de langue si la ligne ne répond que dans une langue précise.
 * `public` : 'etudiants' | 'jeunes' si la ligne vise un public précis.
 */
export const URGENCES = {
  FR: {
    ecoute: { numero: '3114', nom: null, gratuit: true, h24: true },
    autres: [
      { numero: '0 800 73 08 15', nom: 'Écoute CROUS', public: 'etudiants', h24: true },
      { numero: '09 72 39 40 50', nom: 'SOS Amitié', h24: true },
    ],
    urgence: ['15', '112'],
  },
  BE: {
    ecoute: {
      numero: '0800 32 123', nom: 'Centre de Prévention du Suicide',
      langue: 'fr', gratuit: true, h24: true,
    },
    autres: [{ numero: '1813', nom: 'Zelfmoordlijn', langue: 'nl', h24: true }],
    urgence: ['112'],
  },
  CH: {
    ecoute: { numero: '143', nom: 'La Main Tendue', h24: true },
    autres: [{ numero: '147', nom: 'Pro Juventute', public: 'jeunes' }],
    urgence: ['144', '112'],
  },
  LU: {
    ecoute: { numero: '45 45 45', nom: 'SOS Détresse', h24: true },
    urgence: ['112'],
  },
  CA: {
    ecoute: {
      numero: '988',
      nom: { fr: "9-8-8 : Ligne d'aide en cas de crise de suicide", en: '9-8-8 Suicide Crisis Helpline' },
      gratuit: true, h24: true,
    },
    urgence: ['911'],
  },
  US: {
    ecoute: { numero: '988', nom: '988 Suicide & Crisis Lifeline', gratuit: true, h24: true },
    urgence: ['911'],
  },
  GB: {
    ecoute: { numero: '116 123', nom: 'Samaritans', gratuit: true, h24: true },
    urgence: ['999', '112'],
  },
}

/* Fuseau horaire → pays (sert seulement à deviner le pays au premier lancement) */
export const FUSEAUX = {
  // France métropolitaine et outre-mer (le 3114 couvre aussi l'outre-mer)
  'Europe/Paris': 'FR', 'Indian/Reunion': 'FR', 'Indian/Mayotte': 'FR',
  'America/Guadeloupe': 'FR', 'America/Martinique': 'FR', 'America/Cayenne': 'FR',
  'Europe/Brussels': 'BE',
  'Europe/Zurich': 'CH',
  'Europe/Luxembourg': 'LU',
  'Europe/London': 'GB',
  'America/Toronto': 'CA', 'America/Montreal': 'CA', 'America/Vancouver': 'CA',
  'America/Edmonton': 'CA', 'America/Winnipeg': 'CA', 'America/Halifax': 'CA',
  'America/St_Johns': 'CA', 'America/Regina': 'CA', 'America/Moncton': 'CA',
  'America/New_York': 'US', 'America/Chicago': 'US', 'America/Denver': 'US',
  'America/Los_Angeles': 'US', 'America/Phoenix': 'US', 'America/Anchorage': 'US',
  'America/Detroit': 'US', 'Pacific/Honolulu': 'US',
  // Pays sans liste vérifiée : détectés quand même, pour pointer vers la bonne page de l'annuaire
  'Africa/Casablanca': 'MA', 'Africa/Algiers': 'DZ', 'Africa/Tunis': 'TN',
  'Africa/Dakar': 'SN', 'Africa/Abidjan': 'CI', 'Africa/Douala': 'CM',
  'Europe/Berlin': 'DE', 'Europe/Madrid': 'ES', 'Europe/Rome': 'IT',
  'Europe/Lisbon': 'PT', 'Europe/Dublin': 'IE', 'Europe/Amsterdam': 'NL',
}
