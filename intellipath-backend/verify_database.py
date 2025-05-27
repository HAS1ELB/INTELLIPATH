# verify_database.py
from supabase_db import SupabaseDB

def verify_database_setup():
    """Vérifie que la base de données est correctement configurée"""
    try:
        db = SupabaseDB()
        print("✅ Connexion à Supabase établie")
        
        # Vérifier les tables essentielles
        tables_to_check = ['users', 'syllabus', 'modules', 'sessions', 'conversations']
        
        for table in tables_to_check:
            try:
                response = db.supabase.table(table).select('count').execute()
                print(f"✅ Table '{table}' accessible")
            except Exception as e:
                print(f"❌ Problème avec la table '{table}': {e}")
        
        # Vérifier s'il y a des utilisateurs
        try:
            users_response = db.supabase.table('users').select('id, email').limit(5).execute()
            user_count = len(users_response.data) if users_response.data else 0
            print(f"📊 Nombre d'utilisateurs dans la base: {user_count}")
            
            if user_count > 0:
                print("👥 Utilisateurs existants:")
                for user in users_response.data:
                    print(f"   - {user['email']} (ID: {user['id'][:8]}...)")
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la vérification des utilisateurs: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        print("💡 Vérifiez vos variables d'environnement SUPABASE_URL et SUPABASE_KEY")
        return False

if __name__ == "__main__":
    print("🔍 Vérification de la configuration de la base de données\n")
    verify_database_setup()