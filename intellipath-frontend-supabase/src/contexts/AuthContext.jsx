import { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Obtenir la session active lors du chargement
    const getInitialSession = async () => {
      try {
        const { data } = await supabase.auth.getSession();
        setSession(data.session);
        setUser(data.session?.user || null);
      } catch (error) {
        console.error('Erreur lors de la récupération de la session :', error);
      } finally {
        setLoading(false);
      }
    };

    getInitialSession();

    // Configurer l'écouteur pour les changements d'authentification
    const { data: authListener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session);
        setUser(session?.user || null);
        setLoading(false);
      }
    );

    // Nettoyer l'écouteur lors du démontage
    return () => {
      authListener?.subscription?.unsubscribe();
    };
  }, []);

  // Fonction d'inscription
  const signUp = async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signUp({ 
        email, 
        password 
      });
      
      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      console.error('Erreur détaillée:', error);
      // Afficher le message d'erreur spécifique de Supabase
      return { data: null, error: { message: `Erreur: ${error.message || 'Inconnue'}` } };
        }
  };

  // Fonction de connexion
  const signIn = async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ 
        email, 
        password 
      });
      
      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      return { data: null, error };
    }
  };

  // Fonction de déconnexion
  const signOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
    } catch (error) {
      console.error('Erreur lors de la déconnexion :', error);
    }
  };

  // Fonction de mise à jour du profil utilisateur
  const updateProfile = async (profile) => {
    try {
      const { data, error } = await supabase
        .from('users')
        .update(profile)
        .eq('id', user.id)
        .single();
      
      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      return { data: null, error };
    }
  };

  const value = {
    user,
    session,
    signUp,
    signIn,
    signOut,
    updateProfile,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}