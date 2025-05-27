from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
import json

# Chargement des modules personnalisés
from modules.syllabus_generator import generate_syllabus
from modules.teaching_agent import TeachingAgent
from modules.utils import extract_modules_from_syllabus
from modules.quiz_generator import QuizGenerator
from supabase_db import SupabaseDB

# Chargement des variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)  # Activation de CORS pour permettre les requêtes depuis le frontend

# Initialisation de la connexion à Supabase
db = SupabaseDB()

@app.route('/api/syllabus', methods=['POST'])
def create_syllabus():
    """Crée un nouveau syllabus et l'enregistre dans la base de données"""
    # Vérification de l'authentification
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authentification requise"}), 401
    
    # Récupération du token JWT
    token = auth_header.split(' ')[1]
    
    try:
        # Vérifier le token avec Supabase
        user_response = db.supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            return jsonify({"error": "Token invalide"}), 401
        user_id = user_response.user.id
    except Exception as e:
        return jsonify({"error": f"Token invalide: {str(e)}"}), 401
    
    data = request.json
    
    if not data.get('topic'):
        return jsonify({"error": "Le sujet est requis"}), 400
    
    topic = data.get('topic')
    level = data.get('level', 'Intermédiaire')
    duration = data.get('duration', '1 mois')
    learning_style = data.get('learning_style', 'Pratique')
    include_projects = data.get('include_projects', True)
    include_resources = data.get('include_resources', True)
    include_assessments = data.get('include_assessments', True)
    temperature = data.get('temperature', 0.7)
    
    task = f"Générer un syllabus de cours {level.lower()} pour enseigner {topic} sur une durée de {duration}."
    task += f" Adapter le contenu pour un apprenant au style d'apprentissage {learning_style.lower()}."
    
    if include_projects:
        task += " Inclure des projets pratiques."
    if include_resources:
        task += " Inclure des ressources d'apprentissage variées (livres, articles, vidéos, podcasts)."
    if include_assessments:
        task += " Inclure des méthodes d'évaluation progressives."
    
    try:
        # Génération du syllabus
        syllabus_content = generate_syllabus(topic, task, temperature)
        
        # Extraction des modules
        modules = extract_modules_from_syllabus(syllabus_content)
        
        # Sauvegarde du syllabus dans la base de données
        syllabus = db.create_syllabus(
            topic=topic,
            level=level,
            duration=duration,
            learning_style=learning_style,
            content=syllabus_content,
            user_id=user_id,
            include_projects=include_projects,
            include_resources=include_resources,
            include_assessments=include_assessments
        )
        
        if not syllabus:
            return jsonify({"error": "Erreur lors de la création du syllabus"}), 500
        
        # Sauvegarde des modules dans la base de données
        db_modules = db.create_modules(syllabus['id'], modules)
        
        # Création d'une session pour l'utilisateur
        session = db.create_session(user_id, syllabus['id'])
        
        if not session:
            return jsonify({"error": "Erreur lors de la création de la session"}), 500
        
        # Initialiser le suivi de progression
        db.track_progress(
            user_id=user_id,
            syllabus_id=syllabus['id'],
            status='not_started',
            completion_percentage=0
        )
        
        return jsonify({
            'session_id': session['id'],
            'syllabus': syllabus,
            'modules': db_modules,
            'topic': topic
        })
        
    except Exception as e:
        print(f"Erreur lors de la création du syllabus: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/api/conversation/', methods=['POST'])
def conversation(session_id):
    """Gère une conversation avec l'agent d'enseignement"""
    # TEMPORAIREMENT DÉSACTIVÉE POUR LES TESTS - DÉCOMMENTEZ EN PRODUCTION
    # auth_header = request.headers.get('Authorization')
    # if not auth_header or not auth_header.startswith('Bearer '):
    #     return jsonify({"error": "Authentification requise"}), 401
    
    # token = auth_header.split(' ')[1]
    
    # try:
    #     user_response = db.supabase.auth.get_user(token)
    #     if not user_response or not user_response.user:
    #         return jsonify({"error": "Token invalide"}), 401
    #     user_id = user_response.user.id
    # except Exception as e:
    #     return jsonify({"error": f"Token invalide: {str(e)}"}), 401
    
    # POUR LES TESTS : utilisez l'user_id connu
    user_id = "a718a671-3c3b-4ff2-beaf-ef4d8316fae6"  # Remplacez par votre user_id
    
    # Récupération de la session
    session = db.get_session(session_id)
    if not session:
        return jsonify({"error": "Session non trouvée"}), 404
    
    if session['user_id'] != user_id:
        return jsonify({"error": "Accès non autorisé à cette session"}), 403
    
    syllabus_id = session['syllabus_id']
    
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "Message requis"}), 400
    
    try:
        # Récupération du syllabus
        syllabus_data = db.get_syllabus(syllabus_id)
        if not syllabus_data:
            return jsonify({"error": "Syllabus non trouvé"}), 404
        
        # Récupérer la conversation existante ou en créer une nouvelle
        conversation_data = db.get_conversation(user_id, syllabus_id)
        
        if conversation_data and 'messages' in conversation_data:
            messages = conversation_data['messages']
        else:
            messages = []
        
        # Ajouter le message à l'historique
        messages.append({"role": "user", "content": message})
        
        # Initialiser l'agent d'enseignement
        teaching_agent = TeachingAgent()
        teaching_agent.seed_agent(syllabus_data['content'], syllabus_data['topic'])
        
        # Obtenir la réponse de l'agent
        response = teaching_agent.respond(message)
        
        # Ajouter la réponse à l'historique
        messages.append({"role": "assistant", "content": response})
        
        # Mettre à jour la conversation dans la base de données
        db.save_conversation(user_id, syllabus_id, messages)
        
        # Mettre à jour le suivi de progression
        db.track_progress(
            user_id=user_id,
            syllabus_id=syllabus_id,
            status='in_progress',
            completion_percentage=min(100, len(messages) * 5)
        )
        
        return jsonify({
            'response': response,
            'conversation_history': messages
        })
        
    except Exception as e:
        print(f"Erreur lors de la conversation: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/api/quiz/', methods=['POST'])
def generate_quiz(session_id):
    """Génère un quiz et l'enregistre dans la base de données"""
    # TEMPORAIREMENT DÉSACTIVÉE POUR LES TESTS
    user_id = "a718a671-3c3b-4ff2-beaf-ef4d8316fae6"  # Remplacez par votre user_id
    
    # Récupération de la session
    session = db.get_session(session_id)
    if not session:
        return jsonify({"error": "Session non trouvée"}), 404
    
    if session['user_id'] != user_id:
        return jsonify({"error": "Accès non autorisé à cette session"}), 403
    
    syllabus_id = session['syllabus_id']
    
    data = request.json
    module_index = data.get('module_index')
    num_questions = data.get('num_questions', 5)
    difficulty = data.get('difficulty', 'moyen')
    
    try:
        # Récupération du syllabus
        syllabus_data = db.get_syllabus(syllabus_id)
        if not syllabus_data:
            return jsonify({"error": "Syllabus non trouvé"}), 404
        
        # Récupération des modules
        modules = db.get_modules(syllabus_id)
        
        # Déterminer le sujet du quiz et le module_id si applicable
        module_id = None
        if module_index is None:
            quiz_topic = syllabus_data['topic']
            quiz_title = f"Quiz complet sur {quiz_topic}"
        else:
            module_idx = int(module_index)
            if module_idx < 0 or module_idx >= len(modules):
                return jsonify({"error": "Index de module invalide"}), 400
            
            module = modules[module_idx]
            module_id = module['id']
            quiz_topic = module['title']
            quiz_title = f"Quiz sur {quiz_topic}"
        
        # Créer l'entrée du quiz dans la base de données
        quiz = db.create_quiz(
            syllabus_id=syllabus_id,
            title=quiz_title,
            difficulty=difficulty,
            module_id=module_id
        )
        
        if not quiz:
            return jsonify({"error": "Erreur lors de la création du quiz"}), 500
        
        # Générer le quiz
        quiz_generator = QuizGenerator()
        quiz_questions = quiz_generator.generate_quiz(
            topic=quiz_topic,
            difficulty=difficulty,
            num_questions=num_questions
        )
        
        # Convertir les objets Pydantic en dictionnaires
        quiz_dict = []
        for question in quiz_questions:
            quiz_dict.append({
                'question': question.question,
                'options': question.options,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation
            })
        
        # Sauvegarder les questions dans la base de données
        db.create_quiz_questions(quiz['id'], quiz_dict)
        
        return jsonify({
            'quiz_id': quiz['id'],
            'quiz': quiz_dict,
            'topic': quiz_topic
        })
        
    except Exception as e:
        print(f"Erreur lors de la génération du quiz: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/api/quiz/submit/', methods=['POST'])
def submit_quiz(quiz_id):
    """Soumet les réponses d'un quiz et enregistre la tentative"""
    # TEMPORAIREMENT DÉSACTIVÉE POUR LES TESTS
    user_id = "a718a671-3c3b-4ff2-beaf-ef4d8316fae6"  # Remplacez par votre user_id
    
    data = request.json
    answers = data.get('answers', [])
    
    try:
        # Récupération du quiz et de ses questions
        quiz_data = db.get_quiz_with_questions(quiz_id)
        
        if not quiz_data['quiz']:
            return jsonify({"error": "Quiz non trouvé"}), 404
        
        # Calculer le score
        score = 0
        results = []
        
        for i, answer in enumerate(answers):
            if i >= len(quiz_data['questions']):
                break
                
            question = quiz_data['questions'][i]
            is_correct = (answer == question['correct_answer'])
            
            if is_correct:
                score += 1
            
            results.append({
                'question': question['question'],
                'user_answer': question['options'][answer] if answer < len(question['options']) else 'Réponse invalide',
                'correct_answer': question['options'][question['correct_answer']],
                'is_correct': is_correct,
                'explanation': question['explanation']
            })
        
        # Enregistrer la tentative de quiz
        db.record_quiz_attempt(
            user_id=user_id,
            quiz_id=quiz_id,
            score=score,
            total_questions=len(quiz_data['questions']),
            answers=answers
        )
        
        # Mettre à jour la progression de l'utilisateur
        syllabus_id = quiz_data['quiz']['syllabus_id']
        module_id = quiz_data['quiz']['module_id']
        
        # Mise à jour de la progression du module si applicable
        if module_id:
            completion_percentage = (score / len(quiz_data['questions'])) * 100 if quiz_data['questions'] else 0
            db.track_progress(
                user_id=user_id,
                syllabus_id=syllabus_id,
                module_id=module_id,
                status='completed' if completion_percentage >= 70 else 'in_progress',
                completion_percentage=completion_percentage
            )
        
        return jsonify({
            'score': score,
            'total': len(quiz_data['questions']),
            'results': results,
            'percentage': (score / len(quiz_data['questions'])) * 100 if quiz_data['questions'] else 0
        })
        
    except Exception as e:
        print(f"Erreur lors de la soumission du quiz: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/api/session/', methods=['GET'])
def get_session(session_id):
    """Récupère les données d'une session"""
    # TEMPORAIREMENT DÉSACTIVÉE POUR LES TESTS
    user_id = "a718a671-3c3b-4ff2-beaf-ef4d8316fae6"  # Remplacez par votre user_id
    
    try:
        # Récupération de la session
        session = db.get_session(session_id)
        if not session:
            return jsonify({"error": "Session non trouvée"}), 404
        
        if session['user_id'] != user_id:
            return jsonify({"error": "Accès non autorisé à cette session"}), 403
        
        syllabus_id = session['syllabus_id']
        
        # Récupération du syllabus
        syllabus_data = db.get_syllabus(syllabus_id)
        if not syllabus_data:
            return jsonify({"error": "Syllabus non trouvé"}), 404
        
        # Récupération des modules
        modules = db.get_modules(syllabus_id)
        
        # Récupération de la conversation
        conversation_data = db.get_conversation(user_id, syllabus_id)
        conversation_history = conversation_data['messages'] if conversation_data and 'messages' in conversation_data else []
        
        # Récupération de la progression
        progress = db.get_user_progress(user_id, syllabus_id)
        
        return jsonify({
            'topic': syllabus_data['topic'],
            'syllabus': syllabus_data,
            'modules': modules,
            'conversation_history': conversation_history,
            'progress': progress
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération de la session: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/api/user/progress', methods=['GET'])
def get_user_progress():
    """Récupère la progression globale de l'utilisateur"""
    # TEMPORAIREMENT DÉSACTIVÉE POUR LES TESTS
    user_id = "a718a671-3c3b-4ff2-beaf-ef4d8316fae6"  # Remplacez par votre user_id
    
    try:
        # Récupération des syllabus de l'utilisateur
        syllabi = db.get_user_syllabi(user_id)
        
        # Récupération de la progression pour chaque syllabus
        progress_data = []
        
        for syllabus in syllabi:
            # Progression globale du syllabus
            syllabus_progress = db.get_user_progress(user_id, syllabus['id'])
            
            # Filtrer pour obtenir seulement la progression du syllabus (pas des modules)
            overall_progress = next((p for p in syllabus_progress if p['module_id'] is None), None)
            
            if overall_progress:
                progress_data.append({
                    'syllabus_id': syllabus['id'],
                    'topic': syllabus['topic'],
                    'level': syllabus['level'],
                    'status': overall_progress['status'],
                    'completion_percentage': overall_progress['completion_percentage'],
                    'last_activity_at': overall_progress['last_activity_at']
                })
        
        return jsonify({
            'progress': progress_data
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération de la progression: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/api/module//complete', methods=['POST'])
def complete_module(module_id):
    """Marque un module comme complété"""
    # TEMPORAIREMENT DÉSACTIVÉE POUR LES TESTS
    user_id = "a718a671-3c3b-4ff2-beaf-ef4d8316fae6"  # Remplacez par votre user_id
    
    try:
        # Récupération du module
        module = db.get_module(module_id)
        if not module:
            return jsonify({"error": "Module non trouvé"}), 404
        
        syllabus_id = module['syllabus_id']
        
        # Mettre à jour la progression du module
        db.track_progress(
            user_id=user_id,
            syllabus_id=syllabus_id,
            module_id=module_id,
            status='completed',
            completion_percentage=100
        )
        
        # Récupérer tous les modules du syllabus
        all_modules = db.get_modules(syllabus_id)
        
        # Récupérer toutes les progressions des modules pour ce syllabus
        all_modules_progress = db.get_user_progress(user_id, syllabus_id)
        completed_modules = 0
        
        for progress in all_modules_progress:
            if progress['module_id'] and progress['status'] == 'completed':
                completed_modules += 1
        
        # Calculer la progression globale du syllabus
        syllabus_completion = (completed_modules / len(all_modules)) * 100 if all_modules else 0
        
        # Mise à jour de la progression du syllabus
        db.track_progress(
            user_id=user_id,
            syllabus_id=syllabus_id,
            module_id=None,
            status='in_progress' if syllabus_completion < 100 else 'completed',
            completion_percentage=syllabus_completion
        )
        
        return jsonify({
            'module_id': module_id,
            'status': 'completed',
            'syllabus_completion': syllabus_completion
        })
        
    except Exception as e:
        print(f"Erreur lors de la complétion du module: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

# Route de test pour vérifier que le serveur fonctionne
@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifie l'état de santé de l'API"""
    return jsonify({
        'status': 'OK',
        'message': 'IntelliPath API is running',
        'version': '1.0.0'
    })

# Gestionnaire d'erreur global
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint non trouvé'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erreur interne du serveur'}), 500

if __name__ == '__main__':
    print("🚀 Démarrage du serveur IntelliPath...")
    print("📝 URL de l'API: http://localhost:5000")
    print("🏥 Health check: http://localhost:5000/api/health")
    print("🔧 Mode debug activé")
    app.run(debug=True, host='0.0.0.0', port=5000)