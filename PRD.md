# PRD — MediMind

**Version :** 1.0 — document de travail  
**Type de produit :** application web d’accompagnement au bien-être mental  
**Public principal :** étudiants et jeunes adultes  
**Langues de l’interface :** français et anglais  
**Statut :** prototype en développement

---

## 1. Résumé du produit

MediMind est une application web qui permet de discuter avec un assistant conversationnel et de tenir un journal d’humeur. Elle vise à offrir aux étudiants un espace pour exprimer leur ressenti, suivre leur humeur et trouver plus facilement des ressources d’aide humaine.

L’application ne remplace pas un professionnel de santé. Elle ne doit pas être présentée comme un outil de diagnostic, de traitement ou de gestion autonome des urgences.

---

## 2. Contexte et problème

L’idée initiale de MediMind part du constat que certains jeunes rencontrent des difficultés liées au stress, à l’isolement ou à la santé mentale et ne savent pas toujours vers qui se tourner immédiatement.

MediMind cherche à répondre à trois besoins :

1. **Exprimer son ressenti** dans une conversation accessible depuis une interface web.
2. **Suivre son humeur** grâce à des saisies régulières et à un historique.
3. **Identifier une aide humaine** en cas de détresse ou de situation urgente.

Le produit doit éviter de laisser croire qu’une conversation avec une IA équivaut à une prise en charge psychologique.

---

## 3. Public cible

### Public principal

- Étudiants et jeunes adultes.
- Personnes souhaitant utiliser une interface en français ou en anglais.
- Personnes désirant parler de leur quotidien ou suivre leur humeur.

### Point à clarifier

Le formulaire d’inscription partagé recueille une date de naissance. Son utilité doit être définie. Si elle ne répond à aucun besoin produit indispensable, sa collecte doit être réévaluée.

---

## 4. Objectifs et limites

### Objectifs

- Permettre la création d’un compte et la connexion.
- Conserver les conversations et les saisies d’humeur associées à chaque compte.
- Fournir une expérience conversationnelle claire, respectueuse et prudente.
- Permettre de consulter l’humeur du jour, un historique et des statistiques simples.
- Présenter des ressources d’aide humaine adaptées au pays sélectionné.
- Proposer une interface utilisable sur ordinateur et sur mobile, en français et en anglais.

### Ce que MediMind ne promet pas

- Poser un diagnostic médical ou psychologique.
- Remplacer un psychologue, un médecin ou un service d’urgence.
- Détecter avec certitude toutes les situations de crise.
- Garantir une disponibilité permanente : le service dépend notamment du backend et du modèle exécuté avec Ollama.

---

## 5. Évolution de l’idée initiale

| Idée de départ | Orientation du projet présentée dans les échanges |
|---|---|
| Interface React ou Next.js | Interface développée avec Vue.js |
| API GPT ou modèle open source | Modèle `qwen3:4b-instruct` utilisé via Ollama |
| Backend cloud | API FastAPI ; déploiement à définir |
| Chatbot d’accompagnement | Conversations et historique présents dans les extraits |
| Journal de l’humeur | Saisie, historique, filtres et statistiques présents dans les extraits |
| Français et anglais | Configuration `vue-i18n` présentée |
| Analyse d’émotions par NLP | Fonctionnalité distincte non confirmée |
| Mode sécurisé | Logique d’alerte et composants d’aide présents ; efficacité non évaluée |

---

## 6. Parcours utilisateurs

### 6.1 Inscription

1. L’utilisateur ouvre la page d’inscription.
2. Il renseigne les informations demandées.
3. Le backend valide les données et vérifie notamment si l’adresse e-mail est déjà utilisée.
4. Le mot de passe est haché avant stockage.
5. La page confirme la réussite et propose un accès à la connexion.

**Attendu :** les erreurs propres à un champ sont affichées près de celui-ci, en français ou en anglais.

### 6.2 Connexion et déconnexion

1. L’utilisateur saisit son e-mail et son mot de passe.
2. Le backend vérifie les identifiants et crée une session.
3. L’interface récupère les informations du compte connecté.
4. Le nom de l’utilisateur et ses conversations apparaissent sans rechargement manuel.
5. À la déconnexion, la session prend fin et les données de l’ancien compte sont retirées de l’interface.

### 6.3 Conversation avec MediMind

1. L’utilisateur démarre une conversation ou en ouvre une existante.
2. Il écrit un message ou choisit une suggestion.
3. Son message apparaît dans le fil.
4. L’interface signale qu’une réponse est en cours.
5. La réponse de MediMind s’affiche ou, en cas d’échec, une erreur compréhensible est présentée.

Les suggestions visibles dans le code abordent notamment la respiration, le stress, le sommeil et l’anxiété avant un examen.

### 6.4 Journal d’humeur

1. L’utilisateur sélectionne un niveau d’humeur.
2. Il peut ajouter une note et choisir plusieurs causes.
3. Il consulte l’humeur du jour, son historique et des statistiques simples.
4. Une nouvelle saisie le même jour peut remplacer la saisie active précédente.

**Décision métier à prendre :** déterminer si « aujourd’hui » correspond au jour dans le fuseau horaire de l’utilisateur ou au jour UTC. La même règle doit s’appliquer côté backend et côté frontend.

### 6.5 Accès à l’aide humaine

L’utilisateur doit pouvoir consulter des ressources d’aide adaptées au pays sélectionné. En cas de contenu préoccupant, l’interface doit encourager le recours à une aide humaine, sans laisser entendre que l’assistant peut gérer seul une crise.

Ces ressources doivent rester accessibles même si le modèle IA est indisponible.

---

## 7. Exigences fonctionnelles

| ID | Exigence | Priorité | Situation d’après les éléments partagés |
|---|---|---|---|
| F01 | Inscription avec validation et erreurs par champ | Haute | Code présenté |
| F02 | Connexion et déconnexion par session | Haute | Code présenté |
| F03 | Affichage réactif du profil connecté | Haute | Code présenté ; comportement à tester |
| F04 | Protection des routes API privées | Critique | À vérifier sur toutes les routes |
| F05 | Isolation des données par utilisateur | Critique | À vérifier ou compléter |
| F06 | Création et reprise de conversations | Haute | Code présenté |
| F07 | Gestion des réponses en cours et des erreurs | Haute | Code présenté |
| F08 | Saisie et consultation des humeurs | Haute | Code présenté |
| F09 | Historique, filtres et statistiques d’humeur | Moyenne | Code présenté |
| F10 | Interface française et anglaise | Haute | Configuration présentée |
| F11 | Affichage de ressources d’aide selon le pays | Haute | Composants présentés ; couverture à vérifier |
| F12 | Gestion prudente des contenus sensibles | Critique | Logique d’alerte visible ; efficacité à évaluer |
| F13 | Exercices de respiration guidés et structurés | Moyenne | Suggestion présente ; parcours dédié non confirmé |
| F14 | Analyse d’émotions NLP distincte | Basse | Non confirmée |

### Règle d’autorisation indispensable

La vérification de la connexion ne suffit pas. Pour chaque lecture ou modification de conversation, message ou humeur, le backend doit aussi vérifier que la donnée appartient à l’utilisateur connecté.

Cette règle doit notamment être appliquée avant l’appel au modèle IA pour une conversation existante.

---

## 8. Exigences de sécurité et de confidentialité

### Authentification

- Ne jamais enregistrer les mots de passe en clair.
- Utiliser un algorithme de hachage conçu pour les mots de passe.
- Éviter de placer des données sensibles dans le contenu de la session.
- Configurer les cookies et HTTPS de façon adaptée à l’environnement de production.
- Protéger les opérations sensibles contre les requêtes non autorisées.
- Ne pas considérer une garde Vue Router comme une protection suffisante : le contrôle d’accès doit être effectué par l’API.

### Données personnelles

Les conversations et les notes d’humeur peuvent contenir des informations très personnelles. Le projet doit définir :

- quelles données sont collectées ;
- pourquoi elles sont nécessaires ;
- qui peut y accéder ;
- combien de temps elles sont conservées ;
- comment un utilisateur peut demander leur suppression ;
- quelles informations peuvent apparaître dans les journaux techniques.

### Sûreté des réponses IA

- Afficher clairement les limites de MediMind.
- Ne pas présenter les réponses comme des diagnostics.
- Prévoir un comportement lorsque le modèle renvoie une réponse inadaptée ou est indisponible.
- Tester les situations sensibles dans les deux langues.
- Ne pas annoncer qu’un système de détection des crises est fiable avant de l’avoir évalué.

---

## 9. Expérience utilisateur et accessibilité

L’interface doit :

- rester utilisable sur mobile, y compris lorsque l’en-tête manque d’espace ;
- conserver des intitulés accessibles pour les boutons à icône ;
- associer chaque champ de formulaire à son erreur ;
- permettre la navigation au clavier ;
- annoncer les changements importants sans multiplier les messages aux lecteurs d’écran ;
- gérer correctement le focus dans les menus et dialogues ;
- présenter des états distincts pour le chargement, le succès et l’échec ;
- traduire les messages d’erreur et les éléments d’aide, pas seulement les titres.

**Cible d’évaluation :** WCAG 2.2 niveau AA. Cette cible ne vaut pas déclaration de conformité tant que l’interface n’a pas été testée.

### Dates et fuseaux horaires

- Les instants de création peuvent être conservés en UTC puis affichés selon le fuseau de l’utilisateur.
- Une date de naissance est une date civile : elle ne doit pas être décalée par une conversion de fuseau horaire.
- Le calcul de « l’humeur du jour » doit suivre une règle unique, documentée et testée autour de minuit.

---

## 10. Architecture technique

```text
Navigateur
└── Frontend Vue.js
    ├── Vue Router
    ├── vue-i18n : français / anglais
    ├── Pages de conversation et de journal
    └── Appels aux routes /api/...
        └── Backend FastAPI
            ├── Authentification et session
            ├── Conversations et messages
            ├── Journal d’humeur
            ├── Base SQLite
            └── Service IA
                └── Ollama : qwen3:4b-instruct
```

### Éléments non confirmés par les extraits

- Structure finale de toutes les tables et de leurs relations.
- Utilisation effective d’une base de connaissances dans les réponses.
- Stratégie de déploiement.
- Politique de sauvegarde et de restauration.
- Résultats de tests de sécurité, d’accessibilité et de sûreté.

---

## 11. Critères d’acceptation du MVP

Le prototype pourra être considéré comme prêt pour une évaluation encadrée si les scénarios suivants fonctionnent :

1. Un utilisateur peut s’inscrire, se connecter, voir son profil et se déconnecter sans recharger manuellement la page.
2. Une personne non connectée ne peut pas accéder aux routes API privées.
3. Deux comptes distincts ne peuvent pas consulter ou modifier les conversations et les humeurs l’un de l’autre.
4. Les données du compte précédent ne restent pas visibles après une déconnexion ou un changement de compte.
5. Les conversations et le journal restent cohérents après actualisation de la page.
6. Une indisponibilité d’Ollama affiche une erreur compréhensible sans masquer les ressources d’aide.
7. Les scénarios sensibles font l’objet de tests documentés en français et en anglais.
8. Les parcours principaux restent utilisables au clavier et sur un écran mobile étroit.
9. Le calcul de « l’humeur du jour » reste cohérent autour de minuit et dans différents fuseaux horaires.

La satisfaction de ces critères ne constitue **pas** une validation médicale de MediMind.

---

## 12. Priorités de développement

### Priorité 1 — Sécuriser le cœur du produit

- Vérifier les sessions et la protection de toutes les routes privées.
- Associer les données au compte connecté et contrôler leur appartenance.
- Définir une politique de réponse aux situations de détresse.
- Clarifier les limites de l’assistant dans l’interface.

### Priorité 2 — Stabiliser l’expérience

- Corriger et tester l’en-tête mobile.
- Compléter les traductions français/anglais.
- Uniformiser les dates et la notion d’« aujourd’hui ».
- Tester les erreurs réseau, serveur et modèle IA.
- Améliorer la gestion des erreurs de formulaire et du focus.

### Priorité 3 — Préparer les évolutions

- Étudier des exercices guidés structurés.
- Prévoir l’export ou la suppression des données.
- Évaluer l’intérêt réel d’une analyse d’émotions NLP distincte.
- Définir une solution de déploiement et de supervision adaptée à Ollama.

---

## 13. Décisions ouvertes

| Question | Décision attendue |
|---|---|
| À quoi sert la date de naissance ? | Justifier sa collecte ou la retirer |
| Quel fuseau définit « aujourd’hui » ? | Choisir une règle unique backend/frontend |
| Quelles données sont conservées et combien de temps ? | Rédiger une politique de conservation |
| Comment supprimer son compte et ses données ? | Définir le parcours utilisateur et l’API |
| Comment évaluer les réponses dans les situations sensibles ? | Préparer des scénarios et critères de revue |
| Quel environnement hébergera FastAPI, SQLite et Ollama ? | Définir le déploiement |
| L’analyse d’émotions NLP est-elle nécessaire ? | Confirmer son intérêt avant développement |

---

## 14. Références de cadrage

Les références suivantes servent à orienter la conception ; elles ne démontrent pas que le projet les respecte déjà.

- Organisation mondiale de la Santé — *Éthique et gouvernance de l’intelligence artificielle pour la santé*.
- Organisation mondiale de la Santé — informations sur le recours à une aide humaine en situation de crise.
- OWASP — *Password Storage Cheat Sheet*.
- OWASP — *Cross-Site Request Forgery Prevention Cheat Sheet*.
- Starlette — documentation de `SessionMiddleware`.
- W3C — *Web Content Accessibility Guidelines (WCAG) 2.2*.

---

**Synthèse :** MediMind associe conversation IA, journal d’humeur et accès à des ressources humaines. Sa priorité avant une ouverture à des utilisateurs réels est de démontrer la protection des données de chaque compte et la prudence de ses réponses dans les situations sensibles.
