import axios from 'axios';
import { 
  SyllabusFormData, 
  SyllabusResponse, 
  ConversationResponse, 
  QuizResponse, 
  QuizSubmitResponse,
  SessionData
} from '../types';

const API_URL = '/api';

// Créer le syllabus
export const createSyllabus = async (data: SyllabusFormData): Promise<SyllabusResponse> => {
  const response = await axios.post(`${API_URL}/syllabus`, data);
  return response.data;
};

// Envoyer un message à l'agent d'enseignement
export const sendMessage = async (sessionId: string, message: string): Promise<ConversationResponse> => {
  const response = await axios.post(`${API_URL}/conversation/${sessionId}`, { message });
  return response.data;
};

// Générer un quiz
export const generateQuiz = async (
  sessionId: string, 
  moduleIndex: number | null = null,
  numQuestions: number = 5,
  difficulty: string = 'moyen'
): Promise<QuizResponse> => {
  const response = await axios.post(`${API_URL}/quiz/${sessionId}`, {
    module_index: moduleIndex,
    num_questions: numQuestions,
    difficulty
  });
  return response.data;
};

// Soumettre un quiz
export const submitQuiz = async (
  sessionId: string,
  answers: number[],
  quizInfo: any,
  date: string
): Promise<QuizSubmitResponse> => {
  const response = await axios.post(`${API_URL}/quiz/submit/${sessionId}`, {
    answers,
    quiz_info: quizInfo,
    date
  });
  return response.data;
};

// Récupérer les données de session
export const getSessionData = async (sessionId: string): Promise<SessionData> => {
  const response = await axios.get(`${API_URL}/session/${sessionId}`);
  return response.data;
};