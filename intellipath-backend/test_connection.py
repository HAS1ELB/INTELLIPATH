# test_connection.py
from supabase_db import SupabaseDB

def test_connection():
    try:
        db = SupabaseDB()
        print("✅ Connexion à Supabase réussie")
        
        # Test de récupération des tables
        response = db.supabase.table('users').select('count').execute()
        print("✅ Accès aux tables réussi")
        
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    test_connection()