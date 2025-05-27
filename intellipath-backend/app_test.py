from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from supabase_db import SupabaseDB

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialisation de la connexion à Supabase
db = SupabaseDB()

# ID utilisateur fixe pour les tests (remplacez par votre ID)
TEST_USER_ID = "a718a671-3c3b-4ff2-beaf-ef4d8316fae6"

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Récupère les données d'une session - VERSION SIMPLIFIÉE POUR TEST"""
    try:
        # Récupération de la session
        session = db.get_session(session_id)
        if not session:
            return jsonify({"error": "Session non trouvée"}), 404
        
        syllabus_id = session['syllabus_id']
        
        # Récupération du syllabus
        syllabus_data = db.get_syllabus(syllabus_id)
        if not syllabus_data:
            return jsonify({"error": "Syllabus non trouvé"}), 404
        
        # Récupération des modules
        modules = db.get_modules(syllabus_id)
        
        # Récupération de la conversation
        conversation_data = db.get_conversation(TEST_USER_ID, syllabus_id)
        conversation_history = conversation_data['messages'] if conversation_data else []
        
        # Récupération de la progression
        progress = db.get_user_progress(TEST_USER_ID, syllabus_id)
        
        return jsonify({
            'topic': syllabus_data['topic'],
            'syllabus': syllabus_data,
            'modules': modules,
            'conversation_history': conversation_history,
            'progress': progress
        })
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

@app.route('/api/conversation/<session_id>', methods=['POST'])
def conversation(session_id):
    """Gère une conversation - VERSION SIMPLIFIÉE POUR TEST"""
    try:
        # Récupération de la session
        session = db.get_session(session_id)
        if not session:
            return jsonify({"error": "Session non trouvée"}), 404
        
        syllabus_id = session['syllabus_id']
        
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({"error": "Message requis"}), 400
        
        # Récupération du syllabus
        syllabus_data = db.get_syllabus(syllabus_id)
        if not syllabus_data:
            return jsonify({"error": "Syllabus non trouvé"}), 404
        
        # Récupérer la conversation existante ou en créer une nouvelle
        conversation_data = db.get_conversation(TEST_USER_ID, syllabus_id)
        
        if conversation_data:
            messages = conversation_data['messages']
        else:
            messages = []
        
        # Ajouter le message à l'historique
        messages.append({"role": "user", "content": message})
        
        # Réponse simple pour test (à remplacer par votre agent IA)
        if "module 1" in message.lower():
            response = f"Le module 1 du syllabus '{syllabus_data['topic']}' couvre les bases fondamentales. C'est un excellent point de départ pour votre apprentissage."
        else:
            response = f"Je suis votre assistant pour le syllabus '{syllabus_data['topic']}'. Comment puis-je vous aider ?"
        
        # Ajouter la réponse à l'historique
        messages.append({"role": "assistant", "content": response})
        
        # Mettre à jour la conversation dans la base de données
        db.save_conversation(TEST_USER_ID, syllabus_id, messages)
        
        return jsonify({
            'response': response,
            'conversation_history': messages
        })
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification de santé du serveur"""
    return jsonify({"status": "OK", "message": "Serveur IntelliPath opérationnel"})

if __name__ == '__main__':
    print("🚀 Démarrage du serveur IntelliPath...")
    print(f"📍 URL: http://localhost:5000")
    print(f"🔗 Session de test: d29c5099-2ecd-42ad-8316-4b5f4d43e47a")
    app.run(debug=True, host='0.0.0.0', port=5000)
