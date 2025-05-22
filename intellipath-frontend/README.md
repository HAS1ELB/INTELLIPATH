# IntelliPath Frontend

Ce projet constitue le frontend de l'application IntelliPath, un assistant d'apprentissage IA permettant de générer des syllabus personnalisés, d'avoir des conversations éducatives et de passer des quiz.

## Technologies utilisées

- **React** avec **TypeScript** : Pour une UI réactive et typée
- **Vite** : Pour un environnement de développement rapide
- **TailwindCSS** et **DaisyUI** : Pour le design et la mise en page
- **React Router** : Pour la navigation entre les pages
- **Axios** : Pour les appels API vers le backend

## Configuration requise

- Node.js (v14.0.0 ou ultérieur)
- npm (v6.0.0 ou ultérieur)
- Backend IntelliPath en cours d'exécution (voir [instructions du backend](../intellipath-backend/README.md))

## Installation

```bash
# Installation des dépendances
npm install
```

## Démarrage du serveur de développement

```bash
# Démarrer le serveur de développement
npm run dev
```

Le serveur de développement démarrera sur http://localhost:8001

## Fonctionnalités principales

1. **Création de syllabus personnalisés**
   - Définir un sujet d'apprentissage
   - Choisir le niveau, la durée, et le style d'apprentissage
   - Inclure des projets, ressources et évaluations

2. **Conversation avec un agent d'enseignement IA**
   - Poser des questions sur le sujet d'apprentissage
   - Recevoir des explications détaillées
   - Sauvegarder l'historique des conversations

3. **Quiz d'évaluation**
   - Générer des quiz par module ou sur l'ensemble du cours
   - Choisir la difficulté et le nombre de questions
   - Recevoir des feedbacks détaillés sur les réponses
   - Suivre sa progression

## Structure du projet

```
intellipath-frontend/
├── public/               # Fichiers statiques
├── src/
│   ├── components/       # Composants réutilisables
│   ├── contexts/         # Contextes React (gestion d'état global)
│   ├── pages/            # Composants de pages
│   ├── services/         # Services API
│   ├── types/            # Définitions de types TypeScript
│   ├── App.tsx           # Composant racine
│   └── main.tsx          # Point d'entrée
├── index.html            # Template HTML
├── package.json          # Dépendances et scripts
└── vite.config.ts        # Configuration de Vite
```

## Intégration avec le backend

Le frontend communique avec le backend via des appels API REST. La configuration du proxy dans `vite.config.ts` redirige automatiquement les requêtes `/api/*` vers le backend.

Assurez-vous que le backend est en cours d'exécution sur `http://localhost:5000` avant de démarrer le frontend.