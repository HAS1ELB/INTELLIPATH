from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Chargement des modules personnalisés
from modules.syllabus_generator import generate_syllabus
from modules.teaching_agent import TeachingAgent
from modules.utils import extract_modules_from_syllabus
from modules.quiz_generator import QuizGenerator

# Chargement des variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)  # Activation de CORS pour permettre les requêtes depuis le frontend

# Stockage des données de session (à remplacer par une BD en production)
sessions = {}

@app.route('/api/syllabus', methods=['POST'])
def create_syllabus():
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
    
    # Génération du syllabus
    syllabus = generate_syllabus(topic, task, temperature)
    
    # Extraction des modules
    modules = extract_modules_from_syllabus(syllabus)
    
    # Création d'une nouvelle session
    session_id = os.urandom(8).hex()
    teaching_agent = TeachingAgent()
    teaching_agent.seed_agent(syllabus, topic)
    
    sessions[session_id] = {
        'syllabus': syllabus,
        'topic': topic,
        'modules': modules,
        'teaching_agent': teaching_agent,
        'quiz_generator': QuizGenerator(),
        'conversation_history': [],
        'quiz_history': []
    }
    
    return jsonify({
        'session_id': session_id,
        'syllabus': syllabus,
        'modules': modules,
        'topic': topic
    })

@app.route('/api/conversation/<session_id>', methods=['POST'])
def conversation(session_id):
    if session_id not in sessions:
        return jsonify({"error": "Session non trouvée"}), 404
    
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "Message requis"}), 400
    
    # Ajouter le message à l'historique
    sessions[session_id]['conversation_history'].append({"role": "user", "content": message})
    
    # Obtenir la réponse de l'agent
    response = sessions[session_id]['teaching_agent'].respond(message)
    
    # Ajouter la réponse à l'historique
    sessions[session_id]['conversation_history'].append({"role": "assistant", "content": response})
    
    return jsonify({
        'response': response,
        'conversation_history': sessions[session_id]['conversation_history']
    })

@app.route('/api/quiz/<session_id>', methods=['POST'])
def generate_quiz(session_id):
    if session_id not in sessions:
        return jsonify({"error": "Session non trouvée"}), 404
    
    data = request.json
    module_index = data.get('module_index')  # None pour tous les modules
    num_questions = data.get('num_questions', 5)
    difficulty = data.get('difficulty', 'moyen')
    
    # Déterminer le sujet du quiz
    if module_index is None:
        quiz_topic = sessions[session_id]['topic']
    else:
        module_idx = int(module_index)
        if module_idx < 0 or module_idx >= len(sessions[session_id]['modules']):
            return jsonify({"error": "Index de module invalide"}), 400
        
        module = sessions[session_id]['modules'][module_idx]
        quiz_topic = module['title']
    
    # Générer le quiz
    quiz = sessions[session_id]['quiz_generator'].generate_quiz(
        topic=quiz_topic,
        difficulty=difficulty,
        num_questions=num_questions
    )
    
    # Convertir les objets Pydantic en dictionnaires
    quiz_dict = []
    for question in quiz:
        quiz_dict.append({
            'question': question.question,
            'options': question.options,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation
        })
    
    return jsonify({
        'quiz': quiz_dict,
        'topic': quiz_topic
    })

@app.route('/api/quiz/submit/<session_id>', methods=['POST'])
def submit_quiz(session_id):
    if session_id not in sessions:
        return jsonify({"error": "Session non trouvée"}), 404
    
    data = request.json
    answers = data.get('answers', [])
    quiz_info = data.get('quiz_info', {})
    
    # Calculer le score
    score = 0
    results = []
    
    for i, answer in enumerate(answers):
        question = quiz_info.get('quiz')[i]
        is_correct = (answer == question.get('correct_answer'))
        
        if is_correct:
            score += 1
        
        results.append({
            'question': question.get('question'),
            'user_answer': question.get('options')[answer],
            'correct_answer': question.get('options')[question.get('correct_answer')],
            'is_correct': is_correct,
            'explanation': question.get('explanation')
        })
    
    # Ajouter à l'historique
    sessions[session_id]['quiz_history'].append({
        'module': quiz_info.get('topic'),
        'difficulty': quiz_info.get('difficulty', 'moyen'),
        'score': (score / len(answers)) * 100 if answers else 0,
        'date': data.get('date')
    })
    
    return jsonify({
        'score': score,
        'total': len(answers),
        'results': results,
        'quiz_history': sessions[session_id]['quiz_history']
    })

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    if session_id not in sessions:
        return jsonify({"error": "Session non trouvée"}), 404
    
    return jsonify({
        'topic': sessions[session_id]['topic'],
        'syllabus': sessions[session_id]['syllabus'],
        'modules': sessions[session_id]['modules'],
        'conversation_history': sessions[session_id]['conversation_history'],
        'quiz_history': sessions[session_id]['quiz_history']
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)