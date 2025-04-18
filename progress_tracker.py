# Ajout dans un nouveau fichier: progress_tracker.py
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

class ProgressTracker:
    def __init__(self, db_path="user_progress.db"):
        self.db_path = db_path
        self.init_db()
        
    def init_db(self):
        """Initialise la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table pour les quiz complétés
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            topic TEXT,
            score REAL,
            max_score INTEGER,
            completion_time TIMESTAMP
        )
        ''')
        
        # Table pour le temps d'étude
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            topic TEXT,
            duration_minutes INTEGER,
            session_date TIMESTAMP
        )
        ''')
        
        # Table pour les compétences acquises
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            skill_name TEXT,
            proficiency_level INTEGER,
            last_updated TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def record_quiz_result(self, user_id, topic, score, max_score):
        """Enregistre les résultats d'un quiz"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO quiz_results (user_id, topic, score, max_score, completion_time)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, topic, score, max_score, datetime.now()))
        
        conn.commit()
        conn.close()
        
    def record_study_session(self, user_id, topic, duration_minutes):
        """Enregistre une session d'étude"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO study_sessions (user_id, topic, duration_minutes, session_date)
        VALUES (?, ?, ?, ?)
        ''', (user_id, topic, duration_minutes, datetime.now()))
        
        conn.commit()
        conn.close()
        
    def update_skill(self, user_id, skill_name, proficiency_level):
        """Met à jour ou ajoute une compétence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Vérifier si la compétence existe déjà
        cursor.execute('''
        SELECT id FROM skills WHERE user_id = ? AND skill_name = ?
        ''', (user_id, skill_name))
        
        skill = cursor.fetchone()
        
        if skill:
            cursor.execute('''
            UPDATE skills SET proficiency_level = ?, last_updated = ? WHERE id = ?
            ''', (proficiency_level, datetime.now(), skill[0]))
        else:
            cursor.execute('''
            INSERT INTO skills (user_id, skill_name, proficiency_level, last_updated)
            VALUES (?, ?, ?, ?)
            ''', (user_id, skill_name, proficiency_level, datetime.now()))
        
        conn.commit()
        conn.close()
        
    def generate_dashboard(self, user_id, output_dir="dashboard"):
        """Génère un tableau de bord graphique pour l'utilisateur"""
        os.makedirs(output_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        
        # Récupérer les données des quiz
        quiz_df = pd.read_sql('''
        SELECT topic, AVG(score/max_score)*100 as percentage, 
               COUNT(*) as attempts
        FROM quiz_results 
        WHERE user_id = ? 
        GROUP BY topic
        ''', conn, params=(user_id,))
        
        # Récupérer les données de temps d'étude
        study_df = pd.read_sql('''
        SELECT topic, SUM(duration_minutes) as total_minutes
        FROM study_sessions 
        WHERE user_id = ? 
        GROUP BY topic
        ''', conn, params=(user_id,))
        
        # Récupérer les compétences
        skills_df = pd.read_sql('''
        SELECT skill_name, proficiency_level
        FROM skills 
        WHERE user_id = ?
        ''', conn, params=(user_id,))
        
        conn.close()
        
        # Créer les visualisations
        plt.figure(figsize=(12, 8))
        
        # Graphique des performances de quiz
        if not quiz_df.empty:
            plt.subplot(2, 2, 1)
            quiz_df.plot(kind='bar', x='topic', y='percentage', ax=plt.gca())
            plt.title('Performance par sujet (%)')
            plt.ylabel('Score moyen (%)')
            plt.xlabel('Sujet')
            plt.tight_layout()
        
        # Graphique du temps d'étude
        if not study_df.empty:
            plt.subplot(2, 2, 2)
            study_df.plot(kind='pie', y='total_minutes', labels=study_df['topic'], autopct='%1.1f%%', ax=plt.gca())
            plt.title('Répartition du temps d\'étude')
            plt.ylabel('')
        
        # Graphique des compétences
        if not skills_df.empty:
            plt.subplot(2, 2, 3)
            skills_df.plot(kind='barh', x='skill_name', y='proficiency_level', ax=plt.gca())
            plt.title('Niveau de compétence')
            plt.xlabel('Niveau (1-5)')
            plt.ylabel('Compétence')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/{user_id}_dashboard.png")
        plt.close()
        
        return f"{output_dir}/{user_id}_dashboard.png"