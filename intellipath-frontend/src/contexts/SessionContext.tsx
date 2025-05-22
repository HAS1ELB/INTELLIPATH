import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { SyllabusResponse, Module, Message, QuizHistoryItem } from '../types';
import { getSessionData } from '../services/api';

interface SessionContextType {
  sessionId: string | null;
  topic: string | null;
  syllabus: string | null;
  modules: Module[];
  conversationHistory: Message[];
  quizHistory: QuizHistoryItem[];
  loading: boolean;
  error: string | null;
  setSyllabusData: (data: SyllabusResponse) => void;
  updateConversationHistory: (messages: Message[]) => void;
  updateQuizHistory: (quizHistory: QuizHistoryItem[]) => void;
  clearSession: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const SessionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [sessionId, setSessionId] = useState<string | null>(() => {
    const savedSessionId = localStorage.getItem('intellipath_session_id');
    return savedSessionId || null;
  });
  
  const [topic, setTopic] = useState<string | null>(null);
  const [syllabus, setSyllabus] = useState<string | null>(null);
  const [modules, setModules] = useState<Module[]>([]);
  const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
  const [quizHistory, setQuizHistory] = useState<QuizHistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Charger les données de session au démarrage
  useEffect(() => {
    const loadSessionData = async () => {
      if (sessionId) {
        setLoading(true);
        try {
          const data = await getSessionData(sessionId);
          setTopic(data.topic);
          setSyllabus(data.syllabus);
          setModules(data.modules);
          setConversationHistory(data.conversation_history);
          setQuizHistory(data.quiz_history);
        } catch (err) {
          console.error('Erreur lors du chargement de la session:', err);
          setError('Impossible de charger les données de session');
          // Si la session n'existe plus, on la supprime
          clearSession();
        } finally {
          setLoading(false);
        }
      }
    };

    loadSessionData();
  }, [sessionId]);

  // Définir les données du syllabus
  const setSyllabusData = (data: SyllabusResponse) => {
    setSessionId(data.session_id);
    setTopic(data.topic);
    setSyllabus(data.syllabus);
    setModules(data.modules);
    // Réinitialiser l'historique
    setConversationHistory([]);
    setQuizHistory([]);
    // Sauvegarder l'ID de session
    localStorage.setItem('intellipath_session_id', data.session_id);
  };

  // Mettre à jour l'historique de conversation
  const updateConversationHistory = (messages: Message[]) => {
    setConversationHistory(messages);
  };

  // Mettre à jour l'historique des quiz
  const updateQuizHistory = (newQuizHistory: QuizHistoryItem[]) => {
    setQuizHistory(newQuizHistory);
  };

  // Effacer la session
  const clearSession = () => {
    setSessionId(null);
    setTopic(null);
    setSyllabus(null);
    setModules([]);
    setConversationHistory([]);
    setQuizHistory([]);
    localStorage.removeItem('intellipath_session_id');
  };

  return (
    <SessionContext.Provider
      value={{
        sessionId,
        topic,
        syllabus,
        modules,
        conversationHistory,
        quizHistory,
        loading,
        error,
        setSyllabusData,
        updateConversationHistory,
        updateQuizHistory,
        clearSession,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = (): SessionContextType => {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};