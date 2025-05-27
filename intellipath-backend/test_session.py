# test_session.py
from supabase_db import SupabaseDB
import uuid

def create_test_user():
    """Crée un utilisateur de test avec un UUID valide"""
    db = SupabaseDB()
    
    # Générer un UUID valide
    user_id = str(uuid.uuid4())
    email = f"test_{user_id[:8]}@example.com"
    
    try:
        # Insérer directement dans la table users (pour les tests)
        user_data = {
            'id': user_id,
            'email': email,
            'password': 'test_password_hash',  # En production, utilisez un hash
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = db.supabase.table('users').insert(user_data).execute()
        print(f"✅ Utilisateur créé avec l'ID: {user_id}")
        return user_id
        
    except Exception as e:
        print(f"⚠️ Erreur lors de la création de l'utilisateur: {e}")
        print("Tentative de récupération d'un utilisateur existant...")
        
        # Essayer de récupérer un utilisateur existant
        try:
            response = db.supabase.table('users').select('id').limit(1).execute()
            if response.data and len(response.data) > 0:
                existing_id = response.data[0]['id']
                print(f"✅ Utilisation de l'utilisateur existant: {existing_id}")
                return existing_id
            else:
                raise Exception("Aucun utilisateur trouvé")
        except Exception as e2:
            print(f"❌ Impossible de récupérer un utilisateur: {e2}")
            return None

def create_test_session():
    """Crée une session de test complète"""
    db = SupabaseDB()
    
    # Créer ou récupérer un utilisateur
    user_id = create_test_user()
    if not user_id:
        print("❌ Impossible de créer ou récupérer un utilisateur")
        return None
    
    try:
        # Créer un syllabus de test
        print("📚 Création du syllabus de test...")
        syllabus = db.create_syllabus(
            topic="Python pour Débutants",
            level="Débutant",
            duration="2 semaines",
            learning_style="Pratique",
            content="# Python pour Débutants\n\n## Module 1: Introduction\n- Variables\n- Types de données\n\n## Module 2: Structures de contrôle\n- Conditions\n- Boucles",
            user_id=user_id,
            include_projects=True,
            include_resources=True,
            include_assessments=True
        )
        
        print(f"✅ Syllabus créé avec l'ID: {syllabus['id']}")
        
        # Créer une session
        print("🔗 Création de la session...")
        session = db.create_session(user_id, syllabus['id'])
        
        print(f"✅ Session créée avec succès!")
        print(f"📋 Détails de la session:")
        print(f"   - Session ID: {session['id']}")
        print(f"   - User ID: {user_id}")
        print(f"   - Syllabus ID: {syllabus['id']}")
        print(f"\n🚀 Utilisez cette session ID dans votre frontend: {session['id']}")
        
        return session['id']
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la session: {e}")
        return None

def test_session_access(session_id):
    """Teste l'accès à la session créée"""
    if not session_id:
        print("❌ Aucune session à tester")
        return
        
    db = SupabaseDB()
    
    try:
        print(f"\n🔍 Test d'accès à la session: {session_id}")
        session = db.get_session(session_id)
        
        if session:
            print("✅ Session récupérée avec succès!")
            print(f"   - User ID: {session['user_id']}")
            print(f"   - Syllabus ID: {session['syllabus_id']}")
            
            # Tester la récupération du syllabus
            syllabus = db.get_syllabus(session['syllabus_id'])
            if syllabus:
                print(f"✅ Syllabus récupéré: {syllabus['topic']}")
            else:
                print("❌ Erreur lors de la récupération du syllabus")
        else:
            print("❌ Session non trouvée")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    print("🚀 Démarrage du script de test IntelliPath\n")
    
    # Créer une session de test
    session_id = create_test_session()
    
    # Tester l'accès à la session
    test_session_access(session_id)
    
    print("\n✨ Script de test terminé!")
 
