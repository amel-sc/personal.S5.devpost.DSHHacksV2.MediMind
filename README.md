# 🧠 MediMind

**Application web d'accompagnement au bien-être mental pour étudiants et jeunes adultes.**

MediMind permet de discuter avec un assistant conversationnel, de tenir un journal d'humeur et d'accéder plus facilement à des ressources d'aide humaine.

![Statut](https://img.shields.io/badge/statut-prototype-orange)
![Frontend](https://img.shields.io/badge/frontend-Vue.js-42b883)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![IA](https://img.shields.io/badge/IA-Ollama%20%7C%20qwen3:4b--instruct-black)
![Langues](https://img.shields.io/badge/langues-FR%20%7C%20EN-blue)

> ⚠️ **Avertissement important**
> MediMind **n'est pas** un dispositif médical. L'application ne pose aucun diagnostic, ne propose aucun traitement et ne remplace ni un psychologue, ni un médecin, ni un service d'urgence. Elle ne doit pas être utilisée pour gérer seul(e) une situation de crise.
> **En cas de danger immédiat ou de pensées suicidaires, contactez les services d'urgence ou une ligne d'aide de votre pays, ou rapprochez-vous d'une personne de confiance.**

> 🚧 **Projet en développement.** Ce dépôt est un prototype. Il n'a pas encore fait l'objet d'audits de sécurité, d'accessibilité ou de sûreté, et ne doit pas être ouvert à de vrais utilisateurs en l'état.

---

## Sommaire

- [Pourquoi MediMind ?](#pourquoi-medimind-)
- [Fonctionnalités](#fonctionnalités)
- [Ce que MediMind ne fait pas](#ce-que-medimind-ne-fait-pas)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Sécurité et confidentialité](#sécurité-et-confidentialité)
- [Accessibilité](#accessibilité)
- [État d'avancement](#état-davancement)
- [Feuille de route](#feuille-de-route)
- [Questions ouvertes](#questions-ouvertes)
- [Contribuer](#contribuer)
- [Références](#références)
- [English summary](#english-summary)

---

## Pourquoi MediMind ?

Certains jeunes rencontrent des difficultés liées au stress, à l'isolement ou à la santé mentale, sans savoir vers qui se tourner immédiatement. MediMind cherche à répondre à trois besoins :

1. **Exprimer son ressenti** dans une conversation accessible depuis le navigateur.
2. **Suivre son humeur** grâce à des saisies régulières et un historique.
3. **Identifier une aide humaine** en cas de détresse ou de situation urgente.

## Fonctionnalités

- 👤 **Comptes utilisateurs** : inscription, connexion et déconnexion par session, mots de passe hachés.
- 💬 **Conversation avec l'assistant** : création et reprise de conversations, suggestions de départ (respiration, stress, sommeil, anxiété avant un examen), indicateur de réponse en cours, gestion des erreurs.
- 📓 **Journal d'humeur** : niveau d'humeur, note libre, causes multiples, humeur du jour, historique, filtres et statistiques simples.
- 🆘 **Ressources d'aide humaine** selon le pays sélectionné, qui doivent rester accessibles même si le modèle IA est indisponible.
- 🌍 **Interface bilingue** français / anglais (`vue-i18n`).
- 📱 **Responsive** : utilisable sur ordinateur et sur mobile.

## Ce que MediMind ne fait pas

- Poser un diagnostic médical ou psychologique.
- Remplacer un professionnel de santé ou un service d'urgence.
- Détecter avec certitude toutes les situations de crise.
- Garantir une disponibilité permanente : le service dépend du backend et du modèle exécuté avec Ollama.

## Architecture

```text
Navigateur
└── Frontend Vue.js
    ├── Vue Router
    ├── vue-i18n (français / anglais)
    ├── Pages de conversation et de journal
    └── Appels aux routes /api/...
        └── Backend FastAPI
            ├── Authentification et session
            ├── Conversations et messages
            ├── Journal d'humeur
            ├── Base SQLite
            └── Service IA
                └── Ollama : qwen3:4b-instruct
```

| Couche | Technologie |
|---|---|
| Frontend | Vue.js, Vue Router, vue-i18n |
| Backend | FastAPI (sessions via Starlette `SessionMiddleware`) |
| Base de données | SQLite |
| Modèle de langage | `qwen3:4b-instruct` via [Ollama](https://ollama.com) |

## Prérequis

- [Node.js](https://nodejs.org/) (version LTS recommandée)
- [Python](https://www.python.org/) 3.10+
- [Ollama](https://ollama.com/download) installé et lancé

## Installation

> ℹ️ Les commandes ci-dessous sont indicatives : adaptez les noms de dossiers, fichiers et variables à la structure réelle du dépôt.

### 1. Cloner le dépôt

```bash
git clone https://github.com/amel-sc/personal.S5.devpost.DSHHacksV2.MediMind.git
```

### 2. Télécharger le modèle

```bash
ollama pull qwen3:4b-instruct
```

### 3. Lancer le backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # puis renseigner les variables (clé de session, etc.)
uvicorn main:app --reload
```

### 4. Lancer le frontend

```bash
cd frontend
npm install
npm run dev
```

L'application est ensuite accessible à l'adresse indiquée par Vite (généralement `http://localhost:5173`).

## Sécurité et confidentialité

Les conversations et notes d'humeur peuvent contenir des informations très personnelles. Principes retenus :

- Mots de passe **jamais** stockés en clair, hachage dédié aux mots de passe.
- Pas de données sensibles dans le contenu de la session ; cookies et HTTPS configurés pour la production.
- Protection des opérations sensibles contre les requêtes non autorisées (CSRF).
- **Le contrôle d'accès est effectué par l'API**, et non uniquement par les gardes de Vue Router.
- Isolation stricte des données par utilisateur.
- Les réponses de l'IA ne sont jamais présentées comme des diagnostics, et les limites de l'outil sont affichées clairement.

À définir avant toute ouverture à de vrais utilisateurs : données collectées et finalité, durée de conservation, accès, suppression de compte et de données, contenu des journaux techniques.

## Accessibilité

Cible d'évaluation : **WCAG 2.2 niveau AA**. Cette cible ne constitue pas une déclaration de conformité tant que l'interface n'a pas été testée. Points suivis : navigation au clavier, gestion du focus, intitulés des boutons à icône, erreurs associées aux champs, états de chargement / succès / échec distincts, traduction complète des messages.

## État d'avancement

| Fonctionnalité | État |
|---|---|
| Inscription / connexion / déconnexion | Code présent |
| Conversations et historique | Code présent |
| Journal d'humeur, historique, filtres, statistiques | Code présent |
| Interface FR / EN | Configuration présente, traductions à compléter |
| Ressources d'aide par pays | Composants présents, couverture à vérifier |
| Logique d'alerte (contenus sensibles) | Présente, **efficacité non évaluée** |
| Protection de toutes les routes API privées | À vérifier |
| Isolation des données entre comptes | À vérifier / compléter |
| Exercices de respiration guidés | Suggestion uniquement, parcours dédié non confirmé |
| Analyse d'émotions NLP | Non confirmée, intérêt à valider |

### Critères d'acceptation du MVP

Le prototype sera prêt pour une **évaluation encadrée** lorsque :

- [ ] Inscription, connexion, affichage du profil et déconnexion fonctionnent sans rechargement manuel.
- [ ] Un utilisateur non connecté ne peut pas accéder aux routes API privées.
- [ ] Deux comptes ne peuvent pas consulter ou modifier les données l'un de l'autre.
- [ ] Aucune donnée de l'ancien compte ne reste visible après déconnexion ou changement de compte.
- [ ] Conversations et journal restent cohérents après actualisation.
- [ ] Une indisponibilité d'Ollama affiche une erreur compréhensible sans masquer les ressources d'aide.
- [ ] Les scénarios sensibles sont testés et documentés en français et en anglais.
- [ ] Les parcours principaux sont utilisables au clavier et sur mobile.
- [ ] L'« humeur du jour » est cohérente autour de minuit et selon les fuseaux horaires.

> La satisfaction de ces critères ne constitue **pas** une validation médicale.

## Feuille de route

**Priorité 1 : sécuriser le cœur du produit**
- Vérifier les sessions et protéger toutes les routes privées.
- Contrôler l'appartenance des données au compte connecté.
- Définir une politique de réponse aux situations de détresse.
- Clarifier les limites de l'assistant dans l'interface.

**Priorité 2 : stabiliser l'expérience**
- Corriger et tester l'en-tête mobile.
- Compléter les traductions FR / EN.
- Uniformiser les dates et la notion d'« aujourd'hui ».
- Tester les erreurs réseau, serveur et modèle IA.
- Améliorer les erreurs de formulaire et la gestion du focus.

**Priorité 3 : préparer les évolutions**
- Exercices guidés structurés.
- Export et suppression des données.
- Évaluation de l'intérêt d'une analyse d'émotions NLP.
- Solution de déploiement et de supervision adaptée à Ollama.

## Questions ouvertes

- À quoi sert la date de naissance ? (justifier sa collecte ou la retirer)
- Quel fuseau horaire définit « aujourd'hui » ?
- Quelles données conserver, et combien de temps ?
- Comment un utilisateur supprime-t-il son compte et ses données ?
- Comment évaluer les réponses dans les situations sensibles ?
- Quel environnement hébergera FastAPI, SQLite et Ollama ?

## Contribuer

Les contributions sont les bienvenues, en particulier sur la sécurité, l'accessibilité et la sûreté des réponses.

1. Forkez le dépôt et créez une branche (`git checkout -b feature/ma-fonctionnalite`).
2. Commitez vos changements.
3. Ouvrez une Pull Request en décrivant clairement le changement et les tests effectués.

Si vous découvrez une faille de sécurité, merci de **ne pas** ouvrir d'issue publique et de contacter directement le mainteneur.

## Références

Ces références orientent la conception ; elles ne démontrent pas que le projet les respecte déjà.

- OMS, *Éthique et gouvernance de l'intelligence artificielle pour la santé*
- OMS, informations sur le recours à une aide humaine en situation de crise
- OWASP, *Password Storage Cheat Sheet*
- OWASP, *Cross-Site Request Forgery Prevention Cheat Sheet*
- Starlette, documentation de `SessionMiddleware`
- W3C, *Web Content Accessibility Guidelines (WCAG) 2.2*

## English summary

**MediMind** is a web app for student and young-adult mental well-being: a conversational assistant, a mood journal, and country-specific links to human help resources. It is built with **Vue.js** (frontend, `vue-i18n` FR/EN), **FastAPI** (backend), **SQLite**, and a local LLM (`qwen3:4b-instruct`) served by **Ollama**.

MediMind is **not** a medical device and does not provide diagnosis, treatment, or crisis management. This is an early prototype: security, accessibility, and safety evaluations are still pending. If you or someone else is in immediate danger, contact local emergency services or a crisis line.

See the French sections above for architecture, setup, and roadmap.