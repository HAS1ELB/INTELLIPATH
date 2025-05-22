// Types pour le syllabus et modules
export interface Module {
  title: string;
  duration: string;
  description: string;
  topics: string[];
  resources?: string[];
  projects?: string[];
  assessments?: string[];
}

export interface SyllabusResponse {
  session_id: string;
  syllabus: string;
  modules: Module[];
  topic: string;
}

// Types pour la conversation
export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ConversationResponse {
  response: string;
  conversation_history: Message[];
}

// Types pour les quiz
export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
}

export interface QuizResponse {
  quiz: QuizQuestion[];
  topic: string;
}

export interface QuizResult {
  question: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string;
}

export interface QuizSubmitResponse {
  score: number;
  total: number;
  results: QuizResult[];
  quiz_history: QuizHistoryItem[];
}

export interface QuizHistoryItem {
  module: string;
  difficulty: string;
  score: number;
  date: string;
}

// Types pour les sessions
export interface SessionData {
  topic: string;
  syllabus: string;
  modules: Module[];
  conversation_history: Message[];
  quiz_history: QuizHistoryItem[];
}

// Types pour les formulaires
export interface SyllabusFormData {
  topic: string;
  level: 'Débutant' | 'Intermédiaire' | 'Avancé';
  duration: string;
  learning_style: 'Pratique' | 'Théorique' | 'Visuel' | 'Auditif';
  include_projects: boolean;
  include_resources: boolean;
  include_assessments: boolean;
  temperature: number;
}