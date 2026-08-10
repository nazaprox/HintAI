# HintAI

HintAI est une application web éducative basée sur l'intelligence artificielle. Elle aide les élèves à comprendre et résoudre leurs exercices progressivement, tout en leur permettant d'apprendre un concept et de vérifier leur compréhension.

La V1 est conçue pour être déployée directement sur **Vercel**, avec un backend Python et un frontend web léger en HTML/CSS/JavaScript.

---

## 🎯 Fonctionnalités principales

### Help Me

L'élève peut fournir un exercice de plusieurs manières :

* saisir directement le texte ;
* prendre une photo avec la caméra ;
* importer une image ;
* importer un PDF.

Avant tout envoi à l'IA, l'image est analysée localement dans le navigateur avec `analyser.js` et OpenCV.js.

Le contrôle local peut notamment vérifier :

* qualité de l'image ;
* lisibilité ;
* cadrage ;
* orientation ;
* résolution ;
* présence éventuelle de zones problématiques.

Le recadrage et l'amélioration de l'image sont également réalisés localement lorsque cela est possible.

Une fois l'entrée validée, HintAI peut :

1. analyser l'exercice ;
2. fournir un indice 1 ;
3. fournir un indice 2 ;
4. fournir un indice 3 ;
5. répondre aux questions de l'élève ;
6. donner la résolution complète ;
7. proposer un exercice d'évaluation ;
8. analyser le travail de l'élève ;
9. corriger sa réponse ;
10. fournir des indices supplémentaires pour l'exercice d'évaluation.

L'élève peut également demander directement la résolution complète.

Les réponses IA sont transmises progressivement lorsque le streaming est disponible afin d'améliorer l'expérience utilisateur.

---

## 🧠 Learn a Concept

Learn a Concept permet à l'élève d'apprendre un concept plutôt que de simplement résoudre un exercice.

L'élève peut fournir :

* le concept qu'il souhaite apprendre ;
* éventuellement une explication de ce qu'il pense déjà comprendre ;
* éventuellement jusqu'à trois exercices de référence.

L'IA construit ensuite un parcours pédagogique comprenant notamment :

* explication du concept ;
* questions de l'élève ;
* indices ;
* exercice simple ;
* exercice difficile ;
* correction des exercices ;
* nouvelles explications lorsque cela est nécessaire.

L'objectif est de vérifier que l'élève a réellement compris le concept.

---

## 📷 Analyse locale des images

L'analyse initiale des images est effectuée côté navigateur dans `analyser.js`.

OpenCV.js est utilisé pour les opérations locales telles que :

* analyse de qualité ;
* détection du cadrage ;
* correction d'orientation ;
* amélioration ;
* préparation de l'image avant transmission.

Ces opérations locales ne consomment **aucun crédit**.

---

## 💳 Système de crédits

HintAI utilise un système de crédits pour contrôler l'utilisation des fonctionnalités IA.

### Crédits mensuels

| Plan     | Prix mensuel | Crédits |
| -------- | -----------: | ------: |
| Free     |          0 $ |      20 |
| Basic    |          5 $ |      40 |
| Pro      |         10 $ |      80 |
| Pro Plus |         15 $ |     150 |
| Super    |         20 $ |     200 |
| Heavy    |         30 $ |     300 |

### Packs supplémentaires

Les utilisateurs peuvent acheter :

**10 crédits = 1 $**

Les crédits achetés utilisent les mêmes règles de fonctionnement que les crédits Free, notamment concernant les publicités.

---

## 💰 Coût des actions

### Actions gratuites

| Action                                 | Coût |
| -------------------------------------- | ---: |
| Ouvrir Help Me                         |    0 |
| Saisie texte                           |    0 |
| Caméra / prise de photo                |    0 |
| Contrôle qualité OpenCV.js             |    0 |
| Recadrage / amélioration locale        |    0 |
| Ouvrir Learn a Concept                 |    0 |
| Historique local                       |    0 |
| Authentification                       |    0 |
| Consultation de l'historique           |    0 |
| Réaffichage d'une réponse déjà générée |    0 |

### Actions à 0,5 crédit

| Action       | Coût |
| ------------ | ---: |
| Upload image |  0,5 |
| Upload PDF   |  0,5 |

Deux uploads correspondent donc à **1 crédit**.

### Actions à 1 crédit

| Action                                | Coût |
| ------------------------------------- | ---: |
| Indice 1                              |    1 |
| Indice 2                              |    1 |
| Indice 3                              |    1 |
| Question à l'IA                       |    1 |
| Génération d'un exercice d'évaluation |    1 |
| Correction du travail                 |    1 |
| Question sur l'exercice               |    1 |
| Indice sur l'exercice                 |    1 |
| Question pendant Learn a Concept      |    1 |
| Indice pendant Learn a Concept        |    1 |
| Exercice simple                       |    1 |
| Correction d'un exercice              |    1 |
| Nouvelle explication                  |    1 |
| Analyse IA d'un document              |    1 |

### Actions à 2 crédits

| Action                               | Coût |
| ------------------------------------ | ---: |
| Analyse IA initiale Help Me          |    2 |
| Résolution complète                  |    2 |
| Explication initiale Learn a Concept |    2 |
| Exercice difficile                   |    2 |

---

## 📺 Publicités

### Publicité simple

Les utilisateurs Free et les utilisateurs utilisant des crédits achetés peuvent voir des publicités simples entre certaines actions.

* durée : **5 secondes** ;
* récompense : **0 crédit**.

Une publicité simple ne donne donc aucun crédit.

### Rewarded Ads

L'utilisateur peut volontairement regarder une publicité récompensée.

* durée : **15 secondes** ;
* récompense : **+1 crédit**.

Le système de récompense est contrôlé côté serveur afin d'éviter les abus.

---

## 🔥 Bonus de série

HintAI possède un système de série d'activité.

Une journée ne compte que si l'utilisateur réalise réellement une action pédagogique.

Le simple fait d'ouvrir l'application ne valide pas la journée.

### Récompenses

| Série               |  Récompense |
| ------------------- | ----------: |
| 3 jours consécutifs |  +6 crédits |
| 6 jours consécutifs | +12 crédits |

Les règles de validation et les protections anti-abus sont gérées côté backend.

---

## 🔐 Authentification et utilisateurs

Le système utilisateur permet notamment de gérer :

* compte utilisateur ;
* authentification ;
* abonnement ;
* crédits ;
* crédits achetés ;
* bonus de série ;
* récompenses publicitaires ;
* historique ;
* données de session ;
* protections anti-abus.

Les données persistantes nécessaires à l'application sont gérées par `storage.py` et la base de données de la V1.

---

## 🗂️ Historique

L'application conserve un historique local permettant à l'utilisateur de retrouver ses sessions.

L'historique local ne consomme aucun crédit.

Les réponses déjà générées peuvent être consultées sans effectuer une nouvelle requête IA.

---

## 🤖 Intelligence artificielle

Le backend utilise l'API Gemini pour les fonctionnalités d'intelligence artificielle.

Le modèle ciblé pour la V1 est :

`gemini-3.1-flash-lite`

Les appels IA sont centralisés dans :

`ai.py`

La configuration des modèles, paramètres, crédits et limites est centralisée dans :

`config.py`

Le système est conçu pour exploiter le **prompt/context caching** lorsque cela est pertinent afin de réduire les coûts et améliorer les performances.

---

## ⚡ Streaming

HintAI utilise un système de streaming entre le backend et le frontend lorsque la réponse IA peut être transmise progressivement.

Le principe est :

```text
Gemini
   ↓
Backend Python
   ↓
Streaming
   ↓
Frontend
   ↓
Affichage progressif
```

L'objectif est d'éviter d'attendre la génération complète avant d'afficher la réponse.

---

## 🛡️ Protection contre les abus

Le backend doit contrôler notamment :

* consommation des crédits ;
* rewarded ads ;
* bonus de série ;
* achats de crédits ;
* authentification ;
* fréquence des requêtes ;
* tentatives de manipulation du solde ;
* réutilisation frauduleuse des récompenses.

Le solde de crédits ne doit jamais être considéré comme fiable lorsqu'il provient uniquement du frontend.

---

## 📁 Architecture V1

La V1 reste volontairement compacte.

```text
HintAI/
├── ai.py
├── app.py
├── config.py
├── storage.py
├── user.py
├── db
│
├── vercel.json
│
├── index.html
├── style.css
├── analyser.js
└── main.js
```

### Backend

#### `ai.py`

Gère les interactions avec Gemini et la logique IA.

#### `app.py`

Point d'entrée de l'application backend et API HTTP.

#### `config.py`

Centralise :

* configuration de l'application ;
* modèle Gemini ;
* paramètres IA ;
* crédits ;
* prix ;
* abonnements ;
* publicités ;
* rewarded ads ;
* bonus de série ;
* paramètres anti-abus.

#### `storage.py`

Gère la persistance des données.

#### `user.py`

Gère les utilisateurs, abonnements, crédits et données associées.

#### `db`

Stockage des données de la V1.

---

## 🎨 Frontend

### `index.html`

Structure principale de l'application web.

### `style.css`

Interface graphique, responsive design, animations et états de chargement.

### `analyser.js`

Analyse locale des images avec OpenCV.js et préparation des fichiers avant leur transmission au backend.

### `main.js`

Logique principale du frontend, navigation, appels API, streaming et interaction avec l'interface.

---

## 🚀 Déploiement

La V1 est conçue pour être déployée sur Vercel.

Le fichier :

`vercel.json`

définit la configuration nécessaire au déploiement du backend Python et du frontend.

Les secrets et clés API ne doivent jamais être placés directement dans les fichiers source.

La clé Gemini doit être configurée dans les variables d'environnement du projet Vercel.

---

## 🔑 Variables d'environnement

Les valeurs sensibles doivent être configurées dans Vercel.

Exemples :

```text
GEMINI_API_KEY
SECRET_KEY
ENVIRONMENT
HINTAI_VERSION
```

Les valeurs réelles ne doivent jamais être commit dans Git.

---

## 🧪 Développement local

Le backend peut être exécuté localement pour les tests.

Le frontend peut être servi depuis un serveur web local.

Les fonctionnalités dépendant de Vercel ou des variables d'environnement doivent être configurées avant les tests correspondants.

---

## 📌 V1

La priorité de la V1 est :

* Help Me ;
* Learn a Concept ;
* IA Gemini ;
* streaming ;
* analyse locale OpenCV.js ;
* crédits ;
* abonnements ;
* rewarded ads ;
* publicités simples ;
* bonus de série ;
* authentification ;
* historique ;
* protection anti-abus ;
* déploiement Vercel.

---

## 📚 V2 — Mini bibliothèque d'épreuves

Le système de bibliothèque d'épreuves de type mini-Scribd est volontairement réservé à la **V2**.

Il pourra ensuite inclure :

* dépôt d'épreuves ;
* upload de documents ;
* contrôle qualité ;
* classement par niveau ;
* recherche ;
* aperçu ;
* détection des doublons ;
* système de qualité ;
* bibliothèque communautaire.

Cette fonctionnalité n'est pas incluse dans le périmètre de la V1.
