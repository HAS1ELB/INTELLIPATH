# Ajout dans un nouveau fichier: course_recommender.py
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import json
import sqlite3
import pandas as pd

class CourseRecommender:
    def __init__(self, progress_tracker):
        self.llm = OllamaLLM(model="llama3", temperature=0.3)
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
        """Recommande des cours basés sur le profil utilisateur et ses intérêts"""
        user_profile = self.get_user_profile(user_id)
        
        prompt = PromptTemplate(
            template="""En tant qu'agent de recommandation éducative, suggère 5 cours ou ressources d'apprentissage 
            pour un utilisateur avec le profil suivant:
            
            Points forts: {strengths}
            Points faibles: {weaknesses}
            Sujets déjà étudiés: {studied_topics}
            Intérêts exprimés: {interests}
            Objectif professionnel: {career_goal}
            
            Pour chaque cours recommandé, fournis:
            1. Le titre du cours
            2. Une brève description
            3. Les compétences qu'il aide à développer
            4. Son niveau de difficulté (débutant, intermédiaire, avancé)
            5. La raison de cette recommandation basée sur le profil utilisateur
            
            Formate la réponse en JSON avec une liste d'objets pour chaque cours recommandé.
            """,
            input_variables=["strengths", "weaknesses", "studied_topics", "interests", "career_goal"]
        )
        
        formatted_prompt = prompt.format(
            strengths=", ".join(user_profile["strengths"]) or "Aucun identifié",
            weaknesses=", ".join(user_profile["weaknesses"]) or "Aucun identifié",
            studied_topics=", ".join(user_profile["studied_topics"]) or "Aucun identifié",
            interests=interests or "Non spécifié",
            career_goal=career_goal or "Non spécifié"
        )
        
        response = self.llm.invoke(formatted_prompt)
        
        try:
            # Extraction des recommandations du format JSON
            recommendations = json.loads(response)
            return recommendations
        except json.JSONDecodeError:
            # Fallback si le format JSON n'est pas respecté
            print("Erreur de format JSON dans la réponse. Tentative de traitement alternatif.")
            return [{"title": "Erreur de formatage", "description": "Impossible de traiter les recommandations.", "reason": "Erreur technique"}]