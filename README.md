````md
# HintAI

HintAI est une application éducative intelligente qui aide les élèves à résoudre des exercices progressivement grâce à l'intelligence artificielle.

## Fonctionnalités

### Help Me
L'élève peut envoyer :

- Du texte
- Une photo
- Une image depuis la galerie
- Un document PDF

Le contenu passe par un contrôle de qualité avant l'analyse.

L'IA peut ensuite fournir :

1. Indice 1
2. Une réponse à une question de l'élève
3. Indice 2
4. Indice 3
5. La résolution complète

L'élève peut également choisir directement la résolution complète.

Après la résolution, HintAI propose un nouvel exercice pour vérifier que le concept a été compris. L'élève peut soumettre son travail et obtenir une vérification.

### Learn a Competence

L'élève peut apprendre un concept en indiquant éventuellement :

- Jusqu'à 3 exercices
- Ce qu'il a déjà compris du concept

HintAI explique ensuite le concept et propose :

- Un premier exercice accessible
- Un deuxième exercice beaucoup plus difficile

L'élève peut poser des questions et demander des indices progressivement.

### Qualité des documents

Les images et documents peuvent être contrôlés avant leur envoi à l'IA :

- Vérification de la qualité
- Détection d'images floues ou inutilisables
- Recadrage
- Amélioration d'image
- Prévention des documents invalides ou en double

### Streaming

Les réponses de l'IA sont affichées progressivement à l'utilisateur pour améliorer l'expérience et réduire l'impression d'attente.

### Historique

L'historique des exercices et conversations est conservé localement.

### Plans et crédits

Plans prévus :

- Free
- Basic — 5
- Pro — 10
- ProPlus — 15
- Super — 20
- Heavy — 30

Le système prévoit également :

- Des crédits
- Des limites d'utilisation
- Des publicités
- Des publicités récompensées
- Une protection contre les abus
- Un contrôle des coûts
- Du prompt caching lorsque disponible

## Architecture

```text
HintAI/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── ai_service.py
│   ├── image_service.py
│   ├── routes.py
│   └── utils.py
│
├── frontend/
│   ├── App.tsx
│   ├── components.tsx
│   └── styles.ts
│
├── .gitignore
├── requirements.txt
├── README.md
└── vercel.json
````

## Technologies

### Backend

* Python
* FastAPI
* Vercel Serverless Functions
* Google Gemini
* OpenCV
* Pillow
* PyMuPDF

### Frontend

* React Native
* Expo / React Native Web

## Variables d'environnement

La clé Gemini ne doit jamais être ajoutée au dépôt GitHub.

Ajouter dans Vercel :

```text
GEMINI_API_KEY=VOTRE_CLE_ICI
```

## Déploiement sur Vercel

Le projet est connecté à GitHub.

Chaque push vers la branche `main` déclenche automatiquement un nouveau déploiement Vercel.

## Commande unique pour sauvegarder et déployer

Depuis GitHub Codespaces :

```bash
git add . && git commit -m "feat: configure HintAI for Vercel" && git push origin main
```

Après le push, Vercel détecte automatiquement les changements et lance un nouveau déploiement.

## Redéploiement manuel

Si nécessaire :

1. Ouvrir le projet dans Vercel.
2. Aller dans l'onglet **Deployments**.
3. Sélectionner le dernier déploiement.
4. Cliquer sur **Redeploy**.

Pour redéployer après une modification du code, il suffit normalement de faire un nouveau commit et un push sur `main`.

```bash
git add . && git commit -m "update HintAI" && git push origin main
```

## Sécurité

Ne jamais ajouter ces informations dans GitHub :

* `GEMINI_API_KEY`
* Clés API
* Tokens secrets
* Secrets de paiement
* Clés d'administration

Ces valeurs doivent être configurées dans les variables d'environnement de Vercel.

## Versionnement

La branche principale est :

```text
main
```

Le dépôt GitHub sert de source du code et Vercel déploie automatiquement les nouvelles versions après chaque push.

```
```
