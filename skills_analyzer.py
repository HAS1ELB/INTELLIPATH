# Nouveau fichier: skills_analyzer.py
from langchain_ollama import OllamaLLM
import sqlite3
import pandas as pd
import json

class SkillsAnalyzer:
    def __init__(self, progress_tracker):
        self.llm = OllamaLLM(model="llama3", temperature=0.2)
        self.progress_tracker = progress_tracker
    
    def analyze_quiz_performance(self, user_id):
        """Analyse les performances aux quiz pour identifier les forces et faiblesses"""
        conn = sqlite3.connect(self.progress_tracker.db_path)
        
        # Récupérer les résultats de quiz
        quiz_results = pd.read_sql(f"""
        SELECT topic, score, max_score, completion_time
        FROM quiz_results
        WHERE user_id = '{user_id}'
        ORDER BY completion_time DESC
        """, conn)
        
        conn.close()
        
        if quiz_results.empty:
            return {
                "strengths": [],
                "weaknesses": [],
                "analysis": "Pas assez de données pour analyser les performances."
            }
        
        # Calculer les performances par sujet
        quiz_results['percentage'] = quiz_results['score'] / quiz_results['max_score'] * 100
        topic_performance = quiz_results.groupby('topic')['percentage'].mean().reset_index()
        
        # Identifier les forces (>75%) et faiblesses (<50%)
        strengths = topic_performance[topic_performance['percentage'] >= 75]['topic'].tolist()
        weaknesses = topic_performance[topic_performance['percentage'] < 50]['topic'].tolist()
        
        # Analyse plus détaillée avec LLM
        if not quiz_results.empty:
            analysis_prompt = f"""
            Analyse les performances suivantes aux quiz et fournis des recommandations d'amélioration:
            
            {topic_performance.to_string()}
            
            Points forts: {', '.join(strengths) if strengths else 'Aucun identifié'}
            Points faibles: {', '.join(weaknesses) if weaknesses else 'Aucun identifié'}
            
            Fournis:
            1. Une analyse globale des performances
            2. Des recommandations spécifiques pour améliorer les points faibles
            3. Des suggestions pour s'appuyer sur les points forts
            """
            
            analysis = self.llm.invoke(analysis_prompt)
        else:
            analysis = "Pas assez de données pour une analyse détaillée."
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "analysis": analysis
        }
    
    def skill_gap_analysis(self, user_id, target_career=None):
        """Analyse les écarts de compétences pour un objectif professionnel donné"""
        # Récupérer les compétences actuelles
        conn = sqlite3.connect(self.progress_tracker.db_path)
        
        current_skills = pd.read_sql(f"""
        SELECT skill_name, proficiency_level
        FROM skills
        WHERE user_id = '{user_id}'
        """, conn)
        
        conn.close()
        
        current_skills_list = current_skills['skill_name'].tolist() if not current_skills.empty else []
        
        # Si un objectif de carrière est spécifié, analyser l'écart
        if target_career:
            gap_prompt = f"""
            Pour quelqu'un qui souhaite devenir {target_career}, identifie:
            
            1. Les compétences essentielles requises pour cette carrière
            2. Les compétences que l'utilisateur possède déjà: {', '.join(current_skills_list) if current_skills_list else 'Aucune'}
            3. Les compétences manquantes qu'il devrait acquérir
            4. Une suggestion de parcours d'apprentissage pour acquérir ces compétences manquantes
            
            Formate ta réponse en JSON avec les clés: "required_skills", "existing_skills", "missing_skills", "learning_path"
            """
            
            gap_analysis_text = self.llm.invoke(gap_prompt)
            
            try:
                # Tenter de parser le JSON
                gap_analysis = json.loads(gap_analysis_text)
            except json.JSONDecodeError:
                # En cas d'échec, structurer manuellement la réponse
                gap_analysis = {
                    "required_skills": [],
                    "existing_skills": current_skills_list,
                    "missing_skills": [],
                    "learning_path": "Impossible de générer un parcours d'apprentissage automatiquement."
                }
                
            return gap_analysis
        else:
            return {
                "existing_skills": current_skills_list,
                "missing_skills": [],
                "learning_path": "Veuillez spécifier un objectif professionnel pour une analyse complète."
            }