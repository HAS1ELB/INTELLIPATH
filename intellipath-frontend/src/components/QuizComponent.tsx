import { useState } from 'react';
import { useSession } from '../contexts/SessionContext';
import { generateQuiz, submitQuiz } from '../services/api';
import { QuizQuestion, QuizResult } from '../types';

interface QuizComponentProps {
  moduleIndex: number | null;
}

const QuizComponent: React.FC<QuizComponentProps> = ({ moduleIndex }) => {
  const { sessionId, updateQuizHistory } = useSession();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [quizTopic, setQuizTopic] = useState('');
  const [userAnswers, setUserAnswers] = useState<number[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState<QuizResult[]>([]);
  const [score, setScore] = useState<{ score: number; total: number } | null>(null);
  
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('moyen');

  // Charger un quiz pour le module sélectionné ou tous les modules
  const loadQuiz = async () => {
    if (!sessionId) return;
    
    setLoading(true);
    setError(null);
    setSubmitted(false);
    setResults([]);
    setScore(null);
    setUserAnswers([]);
    
    try {
      const response = await generateQuiz(sessionId, moduleIndex, numQuestions, difficulty);
      setQuizQuestions(response.quiz);
      setQuizTopic(response.topic);
      setUserAnswers(new Array(response.quiz.length).fill(-1));
    } catch (err: any) {
      console.error('Erreur lors de la génération du quiz:', err);
      setError(err.response?.data?.error || 'Une erreur est survenue lors de la génération du quiz.');
    } finally {
      setLoading(false);
    }
  };

  // Gérer la soumission du quiz
  const handleSubmit = async () => {
    if (!sessionId || userAnswers.includes(-1)) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const currentDate = new Date().toISOString().slice(0, 16).replace('T', ' ');
      const response = await submitQuiz(
        sessionId,
        userAnswers,
        { quiz: quizQuestions, topic: quizTopic, difficulty },
        currentDate
      );
      
      setResults(response.results);
      setScore({ score: response.score, total: response.total });
      setSubmitted(true);
      updateQuizHistory(response.quiz_history);
    } catch (err: any) {
      console.error('Erreur lors de la soumission du quiz:', err);
      setError(err.response?.data?.error || 'Une erreur est survenue lors de la soumission du quiz.');
    } finally {
      setLoading(false);
    }
  };

  // Gérer la sélection d'une réponse
  const handleAnswerSelect = (questionIndex: number, answerIndex: number) => {
    if (submitted) return;
    
    const newAnswers = [...userAnswers];
    newAnswers[questionIndex] = answerIndex;
    setUserAnswers(newAnswers);
  };

  // Vérifier si toutes les questions ont une réponse
  const allQuestionsAnswered = !userAnswers.includes(-1) && userAnswers.length > 0;

  return (
    <div className="card">
      {!quizQuestions.length ? (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold mb-4">Générer un quiz</h2>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
              <p>{error}</p>
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label htmlFor="numQuestions" className="block mb-2 font-medium">
                Nombre de questions:
              </label>
              <select
                id="numQuestions"
                value={numQuestions}
                onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                className="input-field"
              >
                <option value={3}>3 questions</option>
                <option value={5}>5 questions</option>
                <option value={10}>10 questions</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="difficulty" className="block mb-2 font-medium">
                Difficulté:
              </label>
              <select
                id="difficulty"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="input-field"
              >
                <option value="facile">Facile</option>
                <option value="moyen">Moyen</option>
                <option value="difficile">Difficile</option>
              </select>
            </div>
            
            <button
              onClick={loadQuiz}
              className="btn-primary w-full"
              disabled={loading}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Génération en cours...
                </span>
              ) : (
                `Générer un quiz ${moduleIndex !== null ? 'sur ce module' : 'sur tous les modules'}`
              )}
            </button>
          </div>
        </div>
      ) : submitted ? (
        <div>
          <h2 className="text-2xl font-bold mb-4">Résultats du quiz</h2>
          
          {score && (
            <div className={`p-4 mb-6 rounded-lg text-center ${
              (score.score / score.total) >= 0.7 
                ? 'bg-green-100 text-green-800' 
                : (score.score / score.total) >= 0.4 
                  ? 'bg-yellow-100 text-yellow-800' 
                  : 'bg-red-100 text-red-800'
            }`}>
              <h3 className="text-xl font-bold">Score: {score.score}/{score.total}</h3>
              <p className="mt-1">
                {(score.score / score.total) >= 0.7 
                  ? 'Excellent travail !' 
                  : (score.score / score.total) >= 0.4 
                    ? 'Bon effort. Continuez à progresser !' 
                    : 'Il y a encore du travail à faire. Révisez les notions abordées.'}
              </p>
            </div>
          )}
          
          <div className="space-y-6">
            {results.map((result, index) => (
              <div key={index} className="border rounded-lg overflow-hidden">
                <div className={`p-4 ${result.is_correct ? 'bg-green-50' : 'bg-red-50'}`}>
                  <div className="flex items-start">
                    <div className={`rounded-full p-1 mr-3 ${result.is_correct ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                      {result.is_correct ? (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                    <div>
                      <h4 className="font-medium">{result.question}</h4>
                      <p className="mt-1">
                        <span className="font-medium">Votre réponse:</span> {result.user_answer}
                      </p>
                      {!result.is_correct && (
                        <p className="mt-1 text-green-700">
                          <span className="font-medium">Réponse correcte:</span> {result.correct_answer}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-white">
                  <h5 className="font-medium mb-2">Explication:</h5>
                  <p className="text-gray-700">{result.explanation}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 flex justify-between">
            <button
              onClick={() => {
                setQuizQuestions([]);
                setSubmitted(false);
              }}
              className="btn-secondary"
            >
              Retour
            </button>
            <button
              onClick={loadQuiz}
              className="btn-primary"
            >
              Nouveau quiz
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Quiz: {quizTopic}</h2>
            <span className="text-gray-600 text-sm">Difficulté: {difficulty}</span>
          </div>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
              <p>{error}</p>
            </div>
          )}
          
          <div className="space-y-8">
            {quizQuestions.map((question, qIndex) => (
              <div key={qIndex} className="border rounded-lg p-4 shadow-sm">
                <h3 className="text-lg font-medium mb-3">
                  Question {qIndex + 1}: {question.question}
                </h3>
                <div className="space-y-2">
                  {question.options.map((option, oIndex) => (
                    <div
                      key={oIndex}
                      onClick={() => handleAnswerSelect(qIndex, oIndex)}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        userAnswers[qIndex] === oIndex
                          ? 'border-primary bg-primary bg-opacity-10'
                          : 'border-gray-200 hover:border-primary-light'
                      }`}
                    >
                      <div className="flex items-center">
                        <div className={`h-5 w-5 rounded-full mr-3 flex items-center justify-center border ${
                          userAnswers[qIndex] === oIndex
                            ? 'border-primary bg-primary text-white'
                            : 'border-gray-400'
                        }`}>
                          {userAnswers[qIndex] === oIndex && (
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          )}
                        </div>
                        <span>{option}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-8 flex justify-between">
            <button
              onClick={() => setQuizQuestions([])}
              className="btn-secondary"
            >
              Annuler
            </button>
            <button
              onClick={handleSubmit}
              className="btn-primary"
              disabled={!allQuestionsAnswered || loading}
            >
              {loading ? 'Vérification...' : 'Soumettre'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuizComponent;