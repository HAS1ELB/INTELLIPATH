# IntelliPath Frontend avec Supabase

Ce projet est le frontend de l'application IntelliPath, une plateforme d'apprentissage personnalisée intégrant Supabase comme solution de base de données PostgreSQL.

## Table des matières

- [Technologies utilisées](#technologies-utilisées)
- [Installation](#installation)
- [Configuration](#configuration)
- [Structure du projet](#structure-du-projet)
- [Fonctionnalités](#fonctionnalités)

## Technologies utilisées

- React 18
- Vite
- React Router v6
- Tailwind CSS
- Supabase (Client JavaScript)
- React Markdown

## Installation

1. Clonez ce dépôt :
```bash
git clone <votre-depot>
cd intellipath-frontend-supabase
```

2. Installez les dépendances :
```bash
npm install
```

3. Créez un fichier `.env` à partir du modèle `.env.example` :
```bash
cp .env.example .env
```

4. Remplissez le fichier `.env` avec vos informations Supabase :
```
VITE_SUPABASE_URL=your-project-url.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:5000/api
```

5. Lancez le serveur de développement :
```bash
npm run dev
```

## Configuration

### Supabase

1. Créez un compte sur [Supabase](https://supabase.com/)
2. Créez un nouveau projet
3. Exécutez le script SQL fourni dans le fichier `supabase_schema.sql` dans l'éditeur SQL de Supabase
4. Copiez l'URL et la clé anonyme du projet dans votre fichier `.env`

### Backend

Assurez-vous que le backend IntelliPath avec support Supabase est configuré et en cours d'exécution. Suivez les instructions du guide `SUPABASE_SETUP_GUIDE.md` pour configurer le backend.

## Structure du projet

```
intellipath-frontend-supabase/
├── src/
│   ├── components/      # Composants réutilisables
│   ├── contexts/        # Contextes React (Auth, etc.)
│   ├── lib/             # Bibliothèques et utilitaires
│   ├── pages/           # Pages de l'application
│   ├── services/        # Services API
│   ├── App.jsx          # Composant principal
│   ├── main.jsx         # Point d'entrée
│   └── index.css        # Styles globaux
├── public/              # Fichiers statiques
├── .env.example         # Exemple de fichier d'environnement
├── index.html           # HTML principal
├── vite.config.js       # Configuration Vite
├── tailwind.config.js   # Configuration Tailwind CSS
└── package.json         # Dépendances et scripts
```

## Fonctionnalités

### Authentification
- Inscription et connexion des utilisateurs via Supabase Auth
- Gestion des sessions
- Protection des routes pour les utilisateurs authentifiés

### Syllabus
- Création de syllabus personnalisés
- Affichage des syllabus avec leurs modules
- Suivi de la progression dans un syllabus

### Modules
- Affichage du contenu détaillé des modules
- Marquage des modules comme terminés
- Progression par module

### Quiz
- Génération de quiz par syllabus ou par module
- Interface interactive pour répondre aux questions
- Affichage des résultats et des explications

### Agent d'enseignement
- Interface de chat avec l'agent d'enseignement
- Historique des conversations
- Assistance contextuelle basée sur le syllabus actuel

### Profil utilisateur
- Affichage et modification des informations personnelles
- Statistiques de progression
- Historique des activités récentes