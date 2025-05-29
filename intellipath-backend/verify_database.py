import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def verify_database():
    """Vérifie et crée les tables nécessaires dans Supabase"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Erreur: Variables d'environnement SUPABASE_URL et SUPABASE_KEY manquantes")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connexion à Supabase réussie")
        
        # Vérifier les tables existantes
        tables_to_check = [
            'syllabus', 'modules', 'sessions', 'conversations', 
            'user_progress', 'quizzes', 'quiz_questions', 'quiz_attempts'
        ]
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"✅ Table '{table}' accessible")
            except Exception as e:
                print(f"❌ Table '{table}' inaccessible: {e}")
        
        # Lister toutes les sessions existantes
        try:
            sessions = supabase.table('sessions').select("*").execute()
            print(f"📊 Nombre de sessions trouvées: {len(sessions.data)}")
            
            if sessions.data:
                print("🔍 Sessions existantes:")
                for session in sessions.data[:5]:  # Afficher les 5 premières
                    print(f"   - ID: {session.get('id')}")
                    print(f"     User: {session.get('user_id')}")
                    print(f"     Syllabus: {session.get('syllabus_id')}")
                    print(f"     Créée: {session.get('created_at')}")
                    print()
            else:
                print("⚠️  Aucune session trouvée dans la base de données")
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des sessions: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion à Supabase: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Vérification de la base de données Supabase...")
    verify_database()