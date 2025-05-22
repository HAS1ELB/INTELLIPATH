import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid
from typing import Dict, List, Optional, Any, Union

# Chargement des variables d'environnement
load_dotenv()

class SupabaseDB:
    def __init__(self):
        """Initialise la connexion à Supabase"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Les variables d'environnement SUPABASE_URL et SUPABASE_KEY sont requises")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    # === Méthodes pour les utilisateurs ===
    
    def get_user(self, user_id: str) -> Dict:
        """Récupère les informations d'un utilisateur"""
        return self.supabase.table('users').select('*').eq('id', user_id).single().execute()
    
    def update_user(self, user_id: str, data: Dict) -> Dict:
        """Met à jour les informations d'un utilisateur"""
        return self.supabase.table('users').update(data).eq('id', user_id).execute()
    
    # === Méthodes pour les syllabus ===
    
    def create_syllabus(self, topic: str, level: str, duration: str, learning_style: str,
                        content: str, user_id: str, include_projects: bool = True,
                        include_resources: bool = True, include_assessments: bool = True) -> Dict:
        """Crée un nouveau syllabus dans la base de données"""
        syllabus_data = {
            'topic': topic,
            'level': level,
            'duration': duration,
            'learning_style': learning_style,
            'content': content,
            'include_projects': include_projects,
            'include_resources': include_resources,
            'include_assessments': include_assessments,
            'created_by': user_id
        }
        
        response = self.supabase.table('syllabus').insert(syllabus_data).execute()
        syllabus_id = response.data[0]['id']
        return {'id': syllabus_id, **syllabus_data}
    
    def get_syllabus(self, syllabus_id: str) -> Dict:
        """Récupère un syllabus par son ID"""
        return self.supabase.table('syllabus').select('*').eq('id', syllabus_id).single().execute()
    
    def get_user_syllabi(self, user_id: str) -> List[Dict]:
        """Récupère tous les syllabus d'un utilisateur"""
        # Syllabus créés par l'utilisateur
        created = self.supabase.table('syllabus').select('*').eq('created_by', user_id).execute()
        
        # Syllabus auxquels l'utilisateur est inscrit
        enrolled = self.supabase.table('syllabus')\
            .select('syllabus.*')\
            .join('user_progress', 'syllabus.id', 'user_progress.syllabus_id')\
            .eq('user_progress.user_id', user_id)\
            .execute()
        
        # Combiner et dédupliquer les résultats
        all_syllabi = created.data + enrolled.data
        unique_ids = set()
        result = []
        
        for item in all_syllabi:
            if item['id'] not in unique_ids:
                unique_ids.add(item['id'])
                result.append(item)
        
        return result
    
    # === Méthodes pour les modules ===
    
    def create_modules(self, syllabus_id: str, modules: List[Dict]) -> List[Dict]:
        """Crée plusieurs modules pour un syllabus"""
        modules_data = []
        
        for i, module in enumerate(modules):
            module_data = {
                'syllabus_id': syllabus_id,
                'title': module.get('title', ''),
                'description': module.get('description', ''),
                'content': module.get('content', ''),
                'order_index': i
            }
            modules_data.append(module_data)
        
        response = self.supabase.table('modules').insert(modules_data).execute()
        return response.data
    
    def get_modules(self, syllabus_id: str) -> List[Dict]:
        """Récupère tous les modules d'un syllabus, triés par ordre"""
        return self.supabase.table('modules')\
            .select('*')\
            .eq('syllabus_id', syllabus_id)\
            .order('order_index')\
            .execute()\
            .data
    
    def get_module(self, module_id: str) -> Dict:
        """Récupère un module par son ID"""
        return self.supabase.table('modules').select('*').eq('id', module_id).single().execute()
    
    # === Méthodes pour les quiz ===
    
    def create_quiz(self, syllabus_id: str, title: str, difficulty: str, 
                   module_id: Optional[str] = None) -> Dict:
        """Crée un nouveau quiz dans la base de données"""
        quiz_data = {
            'syllabus_id': syllabus_id,
            'module_id': module_id,
            'title': title,
            'difficulty': difficulty
        }
        
        response = self.supabase.table('quizzes').insert(quiz_data).execute()
        return response.data[0]
    
    def create_quiz_questions(self, quiz_id: str, questions: List[Dict]) -> List[Dict]:
        """Crée plusieurs questions pour un quiz"""
        questions_data = []
        
        for question in questions:
            question_data = {
                'quiz_id': quiz_id,
                'question': question.get('question', ''),
                'options': json.dumps(question.get('options', [])),
                'correct_answer': question.get('correct_answer', 0),
                'explanation': question.get('explanation', '')
            }
            questions_data.append(question_data)
        
        response = self.supabase.table('quiz_questions').insert(questions_data).execute()
        return response.data
    
    def get_quiz_with_questions(self, quiz_id: str) -> Dict:
        """Récupère un quiz et ses questions"""
        quiz = self.supabase.table('quizzes').select('*').eq('id', quiz_id).single().execute().data
        questions = self.supabase.table('quiz_questions').select('*').eq('quiz_id', quiz_id).execute().data
        
        # Convertir les options de JSON string à Python dict
        for q in questions:
            q['options'] = json.loads(q['options'])
        
        return {'quiz': quiz, 'questions': questions}
    
    def record_quiz_attempt(self, user_id: str, quiz_id: str, 
                           score: int, total_questions: int, answers: Dict) -> Dict:
        """Enregistre une tentative de quiz par un utilisateur"""
        attempt_data = {
            'user_id': user_id,
            'quiz_id': quiz_id,
            'score': score,
            'total_questions': total_questions,
            'answers': json.dumps(answers)
        }
        
        response = self.supabase.table('quiz_attempts').insert(attempt_data).execute()
        return response.data[0]
    
    # === Méthodes pour la progression des utilisateurs ===
    
    def track_progress(self, user_id: str, syllabus_id: str, 
                      module_id: Optional[str] = None, 
                      status: str = 'in_progress',
                      completion_percentage: int = 0) -> Dict:
        """Suit la progression d'un utilisateur dans un syllabus ou un module"""
        # Vérifier si une entrée existe déjà
        query = self.supabase.table('user_progress')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('syllabus_id', syllabus_id)
        
        if module_id:
            query = query.eq('module_id', module_id)
        elif module_id is None:
            query = query.is_('module_id', 'null')
        
        existing = query.execute().data
        
        progress_data = {
            'user_id': user_id,
            'syllabus_id': syllabus_id,
            'module_id': module_id,
            'status': status,
            'completion_percentage': completion_percentage,
            'last_activity_at': 'now()'
        }
        
        if existing:
            # Mettre à jour l'entrée existante
            response = self.supabase.table('user_progress')\
                .update(progress_data)\
                .eq('id', existing[0]['id'])\
                .execute()
        else:
            # Créer une nouvelle entrée
            response = self.supabase.table('user_progress')\
                .insert(progress_data)\
                .execute()
        
        return response.data[0]
    
    def get_user_progress(self, user_id: str, syllabus_id: str = None) -> List[Dict]:
        """Récupère la progression d'un utilisateur"""
        query = self.supabase.table('user_progress').select('*').eq('user_id', user_id)
        
        if syllabus_id:
            query = query.eq('syllabus_id', syllabus_id)
        
        return query.execute().data
    
    # === Méthodes pour les conversations ===
    
    def save_conversation(self, user_id: str, syllabus_id: str, messages: List[Dict]) -> Dict:
        """Sauvegarde ou met à jour une conversation"""
        # Vérifier si une conversation existe déjà
        existing = self.supabase.table('conversations')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('syllabus_id', syllabus_id)\
            .execute().data
        
        conversation_data = {
            'user_id': user_id,
            'syllabus_id': syllabus_id,
            'messages': json.dumps(messages),
            'updated_at': 'now()'
        }
        
        if existing:
            # Mettre à jour la conversation existante
            response = self.supabase.table('conversations')\
                .update(conversation_data)\
                .eq('id', existing[0]['id'])\
                .execute()
        else:
            # Créer une nouvelle conversation
            response = self.supabase.table('conversations')\
                .insert(conversation_data)\
                .execute()
        
        return response.data[0]
    
    def get_conversation(self, user_id: str, syllabus_id: str) -> Dict:
        """Récupère une conversation"""
        response = self.supabase.table('conversations')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('syllabus_id', syllabus_id)\
            .single()\
            .execute()
        
        if response.data:
            response.data['messages'] = json.loads(response.data['messages'])
        
        return response.data
    
    # === Méthodes pour les sessions ===
    
    def create_session(self, user_id: str, syllabus_id: str) -> Dict:
        """Crée une nouvelle session"""
        session_data = {
            'user_id': user_id,
            'syllabus_id': syllabus_id
        }
        
        response = self.supabase.table('sessions').insert(session_data).execute()
        return response.data[0]
    
    def get_session(self, session_id: str) -> Dict:
        """Récupère une session par son ID"""
        return self.supabase.table('sessions')\
            .select('*')\
            .eq('id', session_id)\
            .single()\
            .execute()\
            .data