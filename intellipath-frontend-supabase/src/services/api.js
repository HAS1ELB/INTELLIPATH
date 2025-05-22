import { supabase } from '../lib/supabaseClient';

const API_URL = import.meta.env.VITE_API_URL || '/api';

// Fonction utilitaire pour récupérer le token d'authentification
const getAuthHeader = async () => {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

export const api = {
  // Endpoints liés aux syllabus
  syllabus: {
    create: async (syllabusData) => {
      try {
        const headers = await getAuthHeader();
        const response = await fetch(`${API_URL}/syllabus`, {
          method: 'POST',
          headers,
          body: JSON.stringify(syllabusData),
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Erreur lors de la création du syllabus');
        }
        
        return await response.json();
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    },
    
    getUserSyllabi: async () => {
      try {
        // Cette fonction utilise directement Supabase pour récupérer les syllabus de l'utilisateur
        const { data: user } = await supabase.auth.getUser();
        if (!user) throw new Error('Utilisateur non authentifié');
        
        // Récupérer tous les syllabus créés par l'utilisateur
        const { data, error } = await supabase
          .from('syllabus')
          .select('*')
          .eq('created_by', user.user.id);
        
        if (error) throw error;
        return data;
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    },
    
    getById: async (syllabusId) => {
      try {
        // Cette fonction utilise directement Supabase pour récupérer un syllabus spécifique
        const { data, error } = await supabase
          .from('syllabus')
          .select('*')
          .eq('id', syllabusId)
          .single();
        
        if (error) throw error;
        return data;
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    }
  },
  
  // Endpoints liés aux modules
  modules: {
    getModulesBySyllabusId: async (syllabusId) => {
      try {
        // Cette fonction utilise directement Supabase pour récupérer les modules d'un syllabus
        const { data, error } = await supabase
          .from('modules')
          .select('*')
          .eq('syllabus_id', syllabusId)
          .order('order_index', { ascending: true });
        
        if (error) throw error;
        return data;
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    },
    
    getById: async (moduleId) => {
      try {
        // Cette fonction utilise directement Supabase pour récupérer un module spécifique
        const { data, error } = await supabase
          .from('modules')
          .select('*')
          .eq('id', moduleId)
          .single();
        
        if (error) throw error;
        return data;
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    },
    
    completeModule: async (moduleId) => {
      try {
        const headers = await getAuthHeader();
        const response = await fetch(`${API_URL}/module/${moduleId}/complete`, {
          method: 'POST',
          headers,
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Erreur lors de la complétion du module');
        }
        
        return await response.json();
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    }
  },
  
  // Endpoints liés aux quiz
  quiz: {
    generate: async (sessionId, quizData) => {
      try {
        const headers = await getAuthHeader();
        const response = await fetch(`${API_URL}/quiz/${sessionId}`, {
          method: 'POST',
          headers,
          body: JSON.stringify(quizData),
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Erreur lors de la génération du quiz');
        }
        
        return await response.json();
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    },
    
    submit: async (quizId, answersData) => {
      try {
        const headers = await getAuthHeader();
        const response = await fetch(`${API_URL}/quiz/submit/${quizId}`, {
          method: 'POST',
          headers,
          body: JSON.stringify(answersData),
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Erreur lors de la soumission du quiz');
        }
        
        return await response.json();
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    },
    
    getQuizWithQuestions: async (quizId) => {
      try {
        // Cette fonction utilise directement Supabase pour récupérer un quiz et ses questions
        const { data: quiz, error: quizError } = await supabase
          .from('quizzes')
          .select('*')
          .eq('id', quizId)
          .single();
        
        if (quizError) throw quizError;
        
        const { data: questions, error: questionsError } = await supabase
          .from('quiz_questions')
          .select('*')
          .eq('quiz_id', quizId)
          .order('id');
        
        if (questionsError) throw questionsError;
        
        return { quiz, questions };
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    }
  },
  
  // Endpoints liés aux sessions
  session: {
    getSession: async (sessionId) => {
      try {
        const headers = await getAuthHeader();
        const response = await fetch(`${API_URL}/session/${sessionId}`, {
          method: 'GET',
          headers,
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Erreur lors de la récupération de la session');
        }
        
        return await response.json();
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    }
  },
  
  // Endpoints liés à la progression
  progress: {
    getUserProgress: async () => {
      try {
        const headers = await getAuthHeader();
        const response = await fetch(`${API_URL}/user/progress`, {
          method: 'GET',
          headers,
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Erreur lors de la récupération de la progression');
        }
        
        return await response.json();
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    }
  },
  
  // Endpoints liés aux conversations
  conversation: {
    sendMessage: async (sessionId, message) => {
      try {
        const headers = await getAuthHeader();
        const response = await fetch(`${API_URL}/conversation/${sessionId}`, {
          method: 'POST',
          headers,
          body: JSON.stringify({ message }),
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Erreur lors de l\'envoi du message');
        }
        
        return await response.json();
      } catch (error) {
        console.error('Erreur API:', error);
        throw error;
      }
    }
  }
};