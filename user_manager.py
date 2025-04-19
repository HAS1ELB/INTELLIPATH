# user_manager.py
import sqlite3
import hashlib
import uuid
import os
from datetime import datetime, timedelta

class UserManager:
    def __init__(self, db_path="user_auth.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialise la base de données des utilisateurs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table utilisateurs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            salt TEXT,
            created_at TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        ''')
        
        # Table sessions
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            created_at TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password, salt=None):
        """Chiffre un mot de passe avec sel"""
        if salt is None:
            salt = uuid.uuid4().hex
        
        # Utiliser SHA-256 pour le hachage
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        return hashed_password, salt
    
    def register_user(self, username, email, password):
        """Inscrit un nouvel utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vérifier si l'utilisateur existe déjà
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                conn.close()
                return False, "Nom d'utilisateur ou email déjà utilisé"
            
            # Générer l'ID utilisateur et hacher le mot de passe
            user_id = str(uuid.uuid4())
            hashed_password, salt = self._hash_password(password)
            
            # Insérer le nouvel utilisateur
            cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, salt, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, email, hashed_password, salt, datetime.now(), datetime.now()))
            
            conn.commit()
            conn.close()
            
            return True, user_id
        except Exception as e:
            return False, str(e)
    
    def login_user(self, username_or_email, password):
        """Authentifie un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Rechercher l'utilisateur
            cursor.execute(
                "SELECT id, password_hash, salt FROM users WHERE (username = ? OR email = ?) AND is_active = 1", 
                (username_or_email, username_or_email)
            )
            
            user = cursor.fetchone()
            if not user:
                conn.close()
                return False, "Utilisateur non trouvé ou inactif"
            
            user_id, stored_hash, salt = user
            
            # Vérifier le mot de passe
            hashed_password, _ = self._hash_password(password, salt)
            if hashed_password != stored_hash:
                conn.close()
                return False, "Mot de passe incorrect"
            
            # Mettre à jour la date de dernière connexion
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now(), user_id)
            )
            
            # Créer une session
            session_id = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(days=7)  # Session d'une semaine
            
            cursor.execute('''
            INSERT INTO sessions (session_id, user_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            ''', (session_id, user_id, datetime.now(), expires_at))
            
            conn.commit()
            conn.close()
            
            return True, {"user_id": user_id, "session_id": session_id}
        except Exception as e:
            return False, str(e)
    
    def validate_session(self, session_id):
        """Vérifie si une session est valide"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Rechercher la session
            cursor.execute('''
            SELECT s.user_id, u.username, s.expires_at 
            FROM sessions s 
            JOIN users u ON s.user_id = u.id 
            WHERE s.session_id = ?
            ''', (session_id,))
            
            session = cursor.fetchone()
            conn.close()
            
            if not session:
                return False, "Session non trouvée"
            
            user_id, username, expires_at = session
            expires_at = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S.%f')
            
            # Vérifier si la session a expiré
            if expires_at < datetime.now():
                return False, "Session expirée"
            
            return True, {"user_id": user_id, "username": username}
        except Exception as e:
            return False, str(e)
    
    def logout_user(self, session_id):
        """Déconnecte un utilisateur en supprimant sa session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            
            conn.commit()
            conn.close()
            
            return True, "Déconnexion réussie"
        except Exception as e:
            return False, str(e)
    
    def get_user_info(self, user_id):
        """Récupère les informations d'un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT username, email, created_at, last_login FROM users WHERE id = ?", 
                (user_id,)
            )
            
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            username, email, created_at, last_login = user
            
            return True, {
                "user_id": user_id,
                "username": username,
                "email": email,
                "created_at": created_at,
                "last_login": last_login
            }
        except Exception as e:
            return False, str(e)
        
    def reset_password_request(self, email):
        """Génère un token de réinitialisation de mot de passe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vérifier si l'email existe
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "Email non trouvé"
            
            # Générer un token unique
            reset_token = str(uuid.uuid4())
            expiry = datetime.now() + timedelta(hours=24)
            
            # Stocker le token
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_resets (
                token TEXT PRIMARY KEY,
                user_id TEXT,
                expires_at TIMESTAMP,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''')
            
            cursor.execute('''
            INSERT INTO password_resets (token, user_id, expires_at)
            VALUES (?, ?, ?)
            ''', (reset_token, user[0], expiry))
            
            conn.commit()
            conn.close()
            
            # Dans une application réelle, vous enverriez un email avec le lien de réinitialisation
            # Pour ce prototype, nous retournons simplement le token
            return True, reset_token
        except Exception as e:
            return False, str(e)

def reset_password(self, token, new_password):
    """Réinitialise le mot de passe avec un token valide"""
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Vérifier si le token existe et est valide
        cursor.execute('''
        SELECT user_id, expires_at, used FROM password_resets 
        WHERE token = ?
        ''', (token,))
        
        reset = cursor.fetchone()
        if not reset:
            conn.close()
            return False, "Token invalide"
        
        user_id, expires_at, used = reset
        
        # Vérifier si le token a déjà été utilisé
        if used:
            conn.close()
            return False, "Token déjà utilisé"
        
        # Vérifier si le token a expiré
        expires_at = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S.%f')
        if expires_at < datetime.now():
            conn.close()
            return False, "Token expiré"
        
        # Mettre à jour le mot de passe
        hashed_password, salt = self._hash_password(new_password)
        
        cursor.execute('''
        UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
        ''', (hashed_password, salt, user_id))
        
        # Marquer le token comme utilisé
        cursor.execute('''
        UPDATE password_resets SET used = 1 WHERE token = ?
        ''', (token,))
        
        conn.commit()
        conn.close()
        
        return True, "Mot de passe réinitialisé avec succès"
    except Exception as e:
        return False, str(e)

    

    