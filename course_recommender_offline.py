# course_recommender_offline.py
import json
import sqlite3
import pandas as pd
import random

class CourseRecommenderOffline:
    def __init__(self, progress_tracker):
        self.progress_tracker = progress_tracker
        
    def get_user_profile(self, user_id):
        """Récupère le profil de l'utilisateur à partir du tracker de progression"""
        conn = sqlite3.connect(self.progress_tracker.db_path)
        
        # Obtenir les points forts (compétences avec niveau élevé)
        strengths_df = pd.read_sql('''
        SELECT skill_name FROM skills 
        WHERE user_id = ? AND proficiency_level >= 4
        ''', conn, params=(user_id,))
        
        # Obtenir les points faibles (compétences avec niveau bas)
        weaknesses_df = pd.read_sql('''
        SELECT skill_name FROM skills 
        WHERE user_id = ? AND proficiency_level <= 2
        ''', conn, params=(user_id,))
        
        # Obtenir les sujets déjà étudiés
        studied_topics_df = pd.read_sql('''
        SELECT DISTINCT topic FROM study_sessions 
        WHERE user_id = ?
        ''', conn, params=(user_id,))
        
        conn.close()
        
        return {
            "strengths": strengths_df['skill_name'].tolist() if not strengths_df.empty else [],
            "weaknesses": weaknesses_df['skill_name'].tolist() if not weaknesses_df.empty else [],
            "studied_topics": studied_topics_df['topic'].tolist() if not studied_topics_df.empty else []
        }
    
    def recommend_courses(self, user_id, interests=None, career_goal=None):
        """Recommande des cours basés sur le profil utilisateur et ses intérêts - version hors ligne avec données prédéfinies"""
        user_profile = self.get_user_profile(user_id)
        
        # Base de données de cours prédéfinis
        predefined_courses = [
            {
                "title": "Introduction à la Programmation Python",
                "description": "Un cours complet pour débutants en Python couvrant les bases de la programmation.",
                "skills": ["Programmation Python", "Algortihmes de base", "Structures de données"],
                "level": "débutant",
                "reason": "Excellent point de départ pour les débutants en programmation."
            },
            {
                "title": "Data Science avec Python",
                "description": "Apprenez à analyser des données avec pandas, NumPy et matplotlib.",
                "skills": ["Analyse de données", "Visualisation de données", "Python pour la data science"],
                "level": "intermédiaire",
                "reason": "Parfait pour ceux qui souhaitent se spécialiser dans l'analyse de données."
            },
            {
                "title": "Machine Learning: Les Fondamentaux",
                "description": "Une introduction aux concepts et algorithmes d'apprentissage automatique.",
                "skills": ["Machine Learning", "Algorithmes supervisés", "Évaluation de modèles"],
                "level": "intermédiaire",
                "reason": "Idéal pour ceux qui veulent comprendre comment fonctionnent les algorithmes de ML."
            },
            {
                "title": "Deep Learning avec TensorFlow",
                "description": "Création et entraînement de réseaux de neurones profonds pour diverses applications.",
                "skills": ["Deep Learning", "TensorFlow", "Réseaux de neurones"],
                "level": "avancé",
                "reason": "Pour ceux qui souhaitent maîtriser les techniques avancées d'IA."
            },
            {
                "title": "Développement Web Frontend",
                "description": "Apprentissage de HTML, CSS et JavaScript pour créer des sites web interactifs.",
                "skills": ["HTML/CSS", "JavaScript", "Responsive Design"],
                "level": "débutant",
                "reason": "Excellente introduction au développement web frontend."
            },
            {
                "title": "React: Créer des Applications Web Modernes",
                "description": "Développement d'applications web dynamiques avec React et son écosystème.",
                "skills": ["React", "JavaScript moderne", "Gestion d'état"],
                "level": "intermédiaire",
                "reason": "Pour les développeurs web qui souhaitent maîtriser un framework moderne."
            },
            {
                "title": "DevOps et CI/CD",
                "description": "Automatisation du déploiement et de l'intégration continue pour les applications.",
                "skills": ["Docker", "CI/CD", "GitHub Actions"],
                "level": "avancé",
                "reason": "Pour les développeurs qui veulent automatiser le cycle de vie des applications."
            },
            {
                "title": "Cybersécurité: Protéger vos Applications",
                "description": "Comprendre les vulnérabilités et protéger vos applications contre les attaques.",
                "skills": ["Sécurité web", "Cryptographie", "Analyse de vulnérabilités"],
                "level": "intermédiaire",
                "reason": "Essentiel pour tout développeur conscient des enjeux de sécurité."
            },
            {
                "title": "Bases de Données SQL et NoSQL",
                "description": "Maîtrisez les différents types de bases de données et leurs cas d'utilisation.",
                "skills": ["SQL", "MongoDB", "Modélisation de données"],
                "level": "intermédiaire",
                "reason": "Fondamental pour comprendre comment stocker et gérer efficacement les données."
            },
            {
                "title": "Intelligence Artificielle pour l'Entreprise",
                "description": "Applications pratiques de l'IA dans différents secteurs d'activité.",
                "skills": ["IA appliquée", "Études de cas", "Éthique en IA"],
                "level": "intermédiaire",
                "reason": "Idéal pour comprendre la valeur commerciale de l'IA."
            }
        ]
        
        # Ajouter des cours spécifiques aux intérêts si fournis
        if interests:
            interest_keywords = [kw.strip().lower() for kw in interests.split(',')]
            career_keywords = [career_goal.lower()] if career_goal else []
            
            # Filtrer les cours qui correspondent aux intérêts ou à l'objectif de carrière
            recommended_courses = []
            
            for course in predefined_courses:
                # Calcul d'un score de pertinence simple
                relevance_score = 0
                
                # Vérifier si le cours correspond aux points faibles de l'utilisateur
                for weakness in user_profile["weaknesses"]:
                    if any(weakness.lower() in skill.lower() for skill in course["skills"]):
                        relevance_score += 3  # Priorité plus élevée pour combler les lacunes
                
                # Vérifier si le cours correspond aux intérêts de l'utilisateur
                for interest in interest_keywords:
                    if (interest in course["title"].lower() or 
                        interest in course["description"].lower() or 
                        any(interest in skill.lower() for skill in course["skills"])):
                        relevance_score += 2
                
                # Vérifier si le cours correspond à l'objectif de carrière
                for career_kw in career_keywords:
                    if (career_kw in course["title"].lower() or 
                        career_kw in course["description"].lower() or 
                        any(career_kw in skill.lower() for skill in course["skills"])):
                        relevance_score += 2
                
                # Éviter de recommander des sujets déjà étudiés
                if any(topic.lower() in course["title"].lower() for topic in user_profile["studied_topics"]):
                    relevance_score -= 1
                
                # Ajouter un score de pertinence au cours
                course_with_score = course.copy()
                course_with_score["relevance_score"] = relevance_score
                recommended_courses.append(course_with_score)
            
            # Trier par score de pertinence et prendre les 5 premiers
            recommended_courses.sort(key=lambda x: x["relevance_score"], reverse=True)
            top_recommendations = recommended_courses[:5]
            
            # Supprimer le score de pertinence pour l'affichage
            for course in top_recommendations:
                del course["relevance_score"]
                
            return top_recommendations
        else:
            # Si aucun intérêt n'est fourni, sélectionner 5 cours aléatoires
            return random.sample(predefined_courses, min(5, len(predefined_courses)))
