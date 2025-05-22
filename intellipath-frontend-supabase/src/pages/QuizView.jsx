import { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import ReactMarkdown from 'react-markdown';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function QuizView() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Pour les quiz générés sans sauvegarde en base de données
  const stateQuiz = location.state?.quiz;
  const stateTopic = location.state?.topic;
  
  const [quiz, setQuiz] = useState(stateQuiz || null);
  const [topic, setTopic] = useState(stateTopic || '');
  const [quizId, setQuizId] = useState(id || null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [quizResults, setQuizResults] = useState(null);
  const [loading, setLoading] = useState(!stateQuiz);
  const [error, setError] = useState('');

  useEffect(() => {
    // Si le quiz est déjà dans l'état de navigation, ne pas charger depuis l'API
    if (stateQuiz) return;
    
    const fetchQuizData = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const quizData = await api.quiz.getQuizWithQuestions(id);
        setQuiz(quizData.questions);
        setTopic(quizData.quiz.title);
        setQuizId(id);
        
        // Initialiser le tableau des réponses sélectionnées
        setSelectedAnswers(new Array(quizData.questions.length).fill(null));
      } catch (error) {
        console.error('Erreur lors de la récupération du quiz:', error);
        setError('Impossible de charger le quiz');
      } finally {
        setLoading(false);
      }
    };

    fetchQuizData();
  }, [id, stateQuiz]);

  const handleAnswerSelect = (answerIndex) => {
    const newAnswers = [...selectedAnswers];
    newAnswers[currentQuestion] = answerIndex;
    setSelectedAnswers(newAnswers);
  };

  const handleNextQuestion = () => {
    if (currentQuestion < quiz.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmitQuiz = async () => {
    // Vérifier si toutes les questions ont une réponse
    if (selectedAnswers.includes(null)) {
      alert('Veuillez répondre à toutes les questions avant de soumettre le quiz.');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      if (quizId) {
        // Soumettre à l'API si le quiz est sauvegardé en base de données
        const results = await api.quiz.submit(quizId, {
          answers: selectedAnswers,
          quiz_info: { quiz, topic }
        });
        
        setQuizResults(results);
      } else {
        // Calculer les résultats localement si le quiz n'est pas sauvegardé
        const score = selectedAnswers.reduce((total, answer, index) => {
          return answer === quiz[index].correct_answer ? total + 1 : total;
        }, 0);
        
        const results = {
          score,
          total: quiz.length,
          results: quiz.map((question, index) => ({
            question: question.question,
            user_answer: question.options[selectedAnswers[index]],
            correct_answer: question.options[question.correct_answer],
            is_correct: selectedAnswers[index] === question.correct_answer,
            explanation: question.explanation
          }))
        };
        
        setQuizResults(results);
      }
      
      setQuizCompleted(true);
    } catch (error) {
      console.error('Erreur lors de la soumission du quiz:', error);
      setError('Erreur lors de la soumission du quiz');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg">
        {error}
        <div className="mt-4 flex justify-center">
          <Button onClick={() => navigate(-1)}>Retour</Button>
        </div>
      </div>
    );
  }

  if (!quiz || quiz.length === 0) {
    return (
      <div className="text-center">
        <h2 className="text-xl font-medium mb-4 text-gray-900 dark:text-white">Quiz non trouvé</h2>
        <p className="mb-4">Le quiz que vous recherchez n'existe pas ou ne contient aucune question.</p>
        <Button onClick={() => navigate(-1)}>Retour</Button>
      </div>
    );
  }

  // Affichage des résultats si le quiz est terminé
  if (quizCompleted && quizResults) {
    const score = quizResults.score;
    const total = quizResults.total;
    const percentage = Math.round((score / total) * 100);
    const results = quizResults.results || [];
    
    let feedbackText;
    let feedbackColor;
    
    if (percentage >= 80) {
      feedbackText = 'Excellent travail !';
      feedbackColor = 'text-green-600 dark:text-green-400';
    } else if (percentage >= 60) {
      feedbackText = 'Bon travail !';
      feedbackColor = 'text-blue-600 dark:text-blue-400';
    } else {
      feedbackText = 'Continuez à pratiquer !';
      feedbackColor = 'text-yellow-600 dark:text-yellow-400';
    }
    
    return (
      <div className="max-w-3xl mx-auto">
        <Card title="Résultats du quiz">
          <div className="text-center mb-8">
            <h2 className={`text-2xl font-bold mb-2 ${feedbackColor}`}>
              {feedbackText}
            </h2>
            <p className="text-lg mb-4">
              Votre score: <span className="font-bold">{score}/{total}</span> ({percentage}%)
            </p>
            
            {/* Barre de progression */}
            <div className="w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full mb-4">
              <div
                className={`h-full rounded-full ${
                  percentage >= 80 ? 'bg-green-600' : 
                  percentage >= 60 ? 'bg-blue-600' : 
                  'bg-yellow-600'
                }`}
                style={{ width: `${percentage}%` }}
              ></div>
            </div>
          </div>
          
          <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">
            Détail des réponses
          </h3>
          
          <div className="space-y-6">
            {results.map((result, index) => (
              <div 
                key={index}
                className={`p-4 rounded-lg ${
                  result.is_correct 
                    ? 'bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500' 
                    : 'bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500'
                }`}
              >
                <p className="font-medium mb-2">{index + 1}. {result.question}</p>
                <p className="mb-1">
                  <span className="font-medium">Votre réponse:</span> {result.user_answer}
                  {result.is_correct 
                    ? <span className="ml-2 text-green-600 dark:text-green-400">✓</span> 
                    : <span className="ml-2 text-red-600 dark:text-red-400">✗</span>}
                </p>
                {!result.is_correct && (
                  <p className="mb-1">
                    <span className="font-medium">Réponse correcte:</span> {result.correct_answer}
                  </p>
                )}
                {result.explanation && (
                  <div className="mt-2 text-gray-700 dark:text-gray-300">
                    <p className="font-medium mb-1">Explication:</p>
                    <ReactMarkdown>{result.explanation}</ReactMarkdown>
                  </div>
                )}
              </div>
            ))}
          </div>
          
          <div className="mt-8 flex justify-center space-x-4">
            <Button 
              variant="secondary"
              onClick={() => navigate(-1)}
            >
              Retour
            </Button>
            <Link to={`/chat/${quizId || 'general'}`}>
              <Button>
                Discuter avec l'agent
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  // Affichage du quiz en cours
  return (
    <div className="max-w-3xl mx-auto">
      <Card>
        <div className="mb-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Quiz: {topic}
            </h1>
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Question {currentQuestion + 1} sur {quiz.length}
            </span>
          </div>
          
          {/* Barre de progression */}
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full mt-2">
            <div
              className="h-full bg-blue-600 rounded-full"
              style={{ width: `${((currentQuestion + 1) / quiz.length) * 100}%` }}
            ></div>
          </div>
        </div>
        
        <div className="mb-8">
          <h2 className="text-xl font-medium mb-4 text-gray-900 dark:text-white">
            {currentQuestion + 1}. {quiz[currentQuestion].question}
          </h2>
          
          <div className="space-y-3">
            {quiz[currentQuestion].options.map((option, index) => (
              <div
                key={index}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  selectedAnswers[currentQuestion] === index
                    ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-500 dark:border-blue-400'
                    : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
                onClick={() => handleAnswerSelect(index)}
              >
                <div className="flex items-start">
                  <div className={`flex items-center justify-center w-6 h-6 rounded-full mr-3 ${
                    selectedAnswers[currentQuestion] === index
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}>
                    {String.fromCharCode(65 + index)}
                  </div>
                  <div className="flex-1">
                    <ReactMarkdown>{option}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="flex justify-between">
          <Button 
            variant="secondary" 
            onClick={handlePreviousQuestion}
            disabled={currentQuestion === 0}
          >
            Précédent
          </Button>
          
          {currentQuestion < quiz.length - 1 ? (
            <Button 
              variant="primary" 
              onClick={handleNextQuestion}
              disabled={selectedAnswers[currentQuestion] === null}
            >
              Suivant
            </Button>
          ) : (
            <Button 
              variant="primary" 
              onClick={handleSubmitQuiz}
              disabled={isSubmitting || selectedAnswers.includes(null)}
            >
              {isSubmitting ? <LoadingSpinner /> : 'Terminer le quiz'}
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
}