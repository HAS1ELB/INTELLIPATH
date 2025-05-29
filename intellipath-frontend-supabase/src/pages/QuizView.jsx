import { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function QuizView() {
  const { quizId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [quiz, setQuiz] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadQuiz = async () => {
      try {
        setLoading(true);
        
        // Si les données sont passées via l'état de navigation
        if (location.state && location.state.quiz) {
          console.log('📥 Chargement quiz depuis l\'état');
          setQuiz({
            title: location.state.title || 'Quiz',
            topic: location.state.topic || 'Sujet inconnu'
          });
          setQuestions(location.state.quiz);
          setSelectedAnswers(new Array(location.state.quiz.length).fill(null));
        } 
        // Sinon, charger depuis l'API
        else if (quizId && quizId !== 'view') {
          console.log('📥 Chargement quiz depuis l\'API, ID:', quizId);
          const response = await api.quiz.getQuizWithQuestions(quizId);
          setQuiz(response.quiz);
          setQuestions(response.questions);
          setSelectedAnswers(new Array(response.questions.length).fill(null));
        } else {
          setError('Aucun quiz à afficher');
        }
      } catch (error) {
        console.error('❌ Erreur lors du chargement du quiz:', error);
        setError('Erreur lors du chargement du quiz');
      } finally {
        setLoading(false);
      }
    };

    loadQuiz();
  }, [quizId, location.state]);

  const handleAnswerSelect = (answerIndex) => {
    const newAnswers = [...selectedAnswers];
    newAnswers[currentQuestion] = answerIndex;
    setSelectedAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      if (quizId && quizId !== 'view') {
        // Soumettre à l'API si on a un vrai ID
        const response = await api.quiz.submit(quizId, { answers: selectedAnswers });
        setResults(response);
      } else {
        // Calculer les résultats localement
        let score = 0;
        const results = [];
        
        questions.forEach((question, index) => {
          const isCorrect = selectedAnswers[index] === question.correct_answer;
          if (isCorrect) score++;
          
          results.push({
            question: question.question,
            user_answer: question.options[selectedAnswers[index]] || 'Non répondu',
            correct_answer: question.options[question.correct_answer],
            is_correct: isCorrect,
            explanation: question.explanation
          });
        });
        
        setResults({
          score,
          total: questions.length,
          percentage: (score / questions.length) * 100,
          results
        });
      }
      setShowResults(true);
    } catch (error) {
      console.error('❌ Erreur lors de la soumission:', error);
      setError('Erreur lors de la soumission du quiz');
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
      <Card>
        <div className="text-center">
          <div className="text-red-600 mb-4">{error}</div>
          <Button onClick={() => navigate(-1)}>
            Retour
          </Button>
        </div>
      </Card>
    );
  }

  if (showResults) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card title="Résultats du Quiz">
          <div className="mb-6 text-center">
            <div className="text-3xl font-bold mb-2">
              {results.score}/{results.total}
            </div>
            <div className="text-xl text-gray-600">
              {results.percentage.toFixed(1)}%
            </div>
          </div>
          
          <div className="space-y-4">
            {results.results.map((result, index) => (
              <div key={index} className={`p-4 rounded-lg ${result.is_correct ? 'bg-green-50' : 'bg-red-50'}`}>
                <div className="font-semibold mb-2">{result.question}</div>
                <div className="mb-1">
                  <span className="font-medium">Votre réponse:</span> {result.user_answer}
                </div>
                <div className="mb-2">
                  <span className="font-medium">Réponse correcte:</span> {result.correct_answer}
                </div>
                <div className="text-sm text-gray-600">
                  {result.explanation}
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 flex justify-center">
            <Button onClick={() => navigate(-1)}>
              Retour au cours
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <Card>
        <div className="text-center">
          <div className="text-gray-600 mb-4">Aucune question disponible</div>
          <Button onClick={() => navigate(-1)}>
            Retour
          </Button>
        </div>
      </Card>
    );
  }

  const currentQ = questions[currentQuestion];

  return (
    <div className="max-w-4xl mx-auto">
      <Card title={quiz?.title || 'Quiz'}>
        <div className="mb-4 text-sm text-gray-600">
          Question {currentQuestion + 1} sur {questions.length}
        </div>
        
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">{currentQ.question}</h3>
          
          <div className="space-y-2">
            {currentQ.options.map((option, index) => (
              <label key={index} className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name={`question-${currentQuestion}`}
                  value={index}
                  checked={selectedAnswers[currentQuestion] === index}
                  onChange={() => handleAnswerSelect(index)}
                  className="mr-3"
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        </div>
        
        <div className="flex justify-between">
          <Button 
            variant="secondary" 
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
          >
            Précédent
          </Button>
          
          {currentQuestion === questions.length - 1 ? (
            <Button 
              onClick={handleSubmit}
              disabled={selectedAnswers.some(answer => answer === null)}
            >
              Terminer le quiz
            </Button>
          ) : (
            <Button 
              onClick={handleNext}
              disabled={selectedAnswers[currentQuestion] === null}
            >
              Suivant
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
}