# IntelliPath Backend API

Ce projet constitue le backend de l'application IntelliPath, un assistant d'apprentissage IA permettant de générer des syllabus personnalisés, d'avoir des conversations éducatives et de passer des quiz.

## Configuration

1. Créez un fichier `.env` à la racine du projet (vous pouvez copier `.env.example`)
2. Ajoutez votre clé API Groq :
   ```
   GROQ_API_KEY=votre_clé_api_ici
   ```

## Installation

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Démarrage du serveur

```bash
python app.py
```

Le serveur démarrera sur http://localhost:5000

## Endpoints API

### Générer un syllabus
- **POST** `/api/syllabus`
- Body:
  ```json
  {
    "topic": "Machine Learning",
    "level": "Débutant",
    "duration": "1 mois",
    "learning_style": "Pratique",
    "include_projects": true,
    "include_resources": true,
    "include_assessments": true,
    "temperature": 0.7
  }
  ```

### Conversation avec l'instructeur
- **POST** `/api/conversation/:session_id`
- Body:
  ```json
  {
    "message": "Pouvez-vous m'expliquer le concept de régression linéaire?"
  }
  ```

### Générer un quiz
- **POST** `/api/quiz/:session_id`
- Body:
  ```json
  {
    "module_index": 1,  // null pour tous les modules
    "num_questions": 5,
    "difficulty": "moyen"
  }
  ```

### Soumettre un quiz
- **POST** `/api/quiz/submit/:session_id`
- Body:
  ```json
  {
    "answers": [0, 2, 1, 3],
    "quiz_info": {
      "quiz": [...],
      "topic": "Machine Learning",
      "difficulty": "moyen"
    },
    "date": "2023-05-21 14:30"
  }
  ```

### Récupérer les données d'une session
- **GET** `/api/session/:session_id`