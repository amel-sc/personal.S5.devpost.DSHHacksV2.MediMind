# MediMind
## Définition
- MediMind est un outil de soutien et d’éducation, pas un thérapeute. Il ne pose pas de diagnostic, ne parle pas de médicaments, ne remplace pas un professionnel
- Le public cible : étudiants/jeunes, français + anglais.
- chat, exercices de respiration, journal d’humeur, orientation vers de l’aide humaine. Tout le reste (analyse d’émotions avancée, etc.) vient après.
- NLP (Natural Language Processing) : Traitement Automatique du Langage Naturel, permet aux machines de comprendre, d'interpréter et de générer le langage humain.

## A faire
- Journal de bord de l'humeur (Pour l'utilisateur, sans IA nécessaire)
    - choisi son humeur (échelle de 1 à 5 : très bien, bien, bof, mal, très mal) : radio
    - peut ajouter une note libre : textarea
    - peut cocher des facteurs : checkbox
- Afficher les statistiques des humeurs : courbe
- Analyse des émotions par NLP (du message de l'utilisateur) et adapter la réponse de l'IA selon l'émotion
- Avertissement clair dans l’interface : « MediMind n’est pas un service médical ni d’urgence ».
- Limites de session et de contenu : évite que le bot encourage une dépendance (rappeler régulièrement qu’il complète, sans remplacer, l’aide humaine).

## Présentation
- Le mode sécurisé à deux couches
- L’adaptation du ton selon l’émotion détectée (tu peux commencer simplement : demander l’humeur en début de session, puis adapter)
- Le multilingue
- L’évaluation de la sécurité avec un jeu de tests (rare dans les projets étudiants, ça te démarquera)

## A rectifier
1. Historique reconstruit côté serveur. Aujourd'hui, le front envoie historique, donc n'importe qui peut injecter de faux messages « assistant ». Relis plutôt les 12 derniers messages en base à partir de id_conversation.
2. Alerte enregistrée en base. Ajoute une colonne alerte à la table message. Sinon, l'encadré AideUrgence disparaît quand on recharge la conversation.
3. Bibliothèque d'exercices validée par le psychologue. La respiration, l'ancrage 5-4-3-2-1, etc. seraient stockés en JSON, avec un exercice guidé et animé côté front, au lieu d'être générés par le LLM. Ce sera plus fiable et plus parlant pour ta démo.
4. Lien avec le journal d'humeur. Passe l'humeur du jour au prompt (« humeur du jour : 4/5, causes : examens »). C'est une vraie intégration entre tes fonctionnalités.
5. Jeu d'évaluation. Constitue 100 à 200 messages annotés par le psychologue de l'équipe (risque, hors sujet, physique, normal, en FR et en EN). Objectif : 100 % de rappel sur le risque, en acceptant quelques fausses alertes. C'est un excellent argument pour ta soutenance.
6. Troisième couche de modération (option). Un modèle dédié comme llama-guard3:1b sur Ollama, qui possède une catégorie « automutilation », peut vérifier les messages et les réponses.
7. Streaming (stream=True + SSE). Sur un modèle local, voir le texte arriver mot à mot réduit beaucoup l'attente perçue.
8. RGPD. Ce sont des données de santé (article 9). Il te faut un consentement explicite, une mention « je suis une IA » visible et une suppression possible des conversations. Ne journalise jamais le contenu des messages : le code ci-dessus ne journalise que le type et le niveau. Le LLM local est un vrai atout sur ce point.
9. Fuseau envoyé par le front. Le bloc « il est tard » utilise l'heure de Paris, ce qui est faux pour un étudiant à Montréal.