import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function QuizCreator() {
  const { sessionId } = useParams();
  const [searchParams] = useSearchParams();
  const moduleId = searchParams.get('module');
  const navigate = useNavigate();
  
  const [syllabus, setSyllabus] = useState(null);
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    module_index: moduleId ? null : -1, // -1 pour tout le syllabus, ou l'index spécifique d'un module
    num_questions: 5,
    difficulty: 'moyen'
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Dans un système réel, récupérez la session et le syllabus associé
        try {
          const sessionData = await api.session.getSession(sessionId);
          
          if (sessionData.syllabus) {
            setSyllabus(sessionData.syllabus);
          }
          
          if (sessionData.modules) {
            setModules(sessionData.modules);
            
            // Si un moduleId est spécifié dans l'URL, trouvez son index
            if (moduleId) {
              const moduleIndex = sessionData.modules.findIndex(m => m.id === moduleId);
              if (moduleIndex !== -1) {
                setFormData(prev => ({ ...prev, module_index: moduleIndex }));
              }
            }
          }
        } catch (error) {
          console.error('Erreur lors de la récupération de la session:', error);
          setError('Impossible de récupérer les informations de session');
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des données:', error);
        setError('Impossible de charger les données');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [sessionId, moduleId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'num_questions' ? parseInt(value) : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGenerating(true);
    setError('');

    try {
      // Convertir module_index de -1 à null si nécessaire (pour tout le syllabus)
      const quizData = {
        ...formData,
        module_index: formData.module_index === -1 ? null : formData.module_index
      };
      
      const response = await api.quiz.generate(sessionId, quizData);
      
      if (response.quiz_id) {
        navigate(`/quiz/${response.quiz_id}`);
      } else {
        navigate(`/quiz/view`, { state: { quiz: response.quiz, topic: response.topic } });
      }
    } catch (error) {
      console.error('Erreur lors de la génération du quiz:', error);
      setError('Une erreur est survenue lors de la génération du quiz');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card title="Générer un quiz">
        {error && (
          <div className="mb-6 p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Sujet du quiz
            </label>
            <select
              name="module_index"
              value={formData.module_index}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              disabled={moduleId !== null}
            >
              <option value={-1}>Tout le syllabus</option>
              {modules.map((module, index) => (
                <option key={module.id} value={index}>
                  {module.title}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Difficulté
            </label>
            <select
              name="difficulty"
              value={formData.difficulty}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="facile">Facile</option>
              <option value="moyen">Moyen</option>
              <option value="difficile">Difficile</option>
            </select>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Nombre de questions
            </label>
            <input
              type="number"
              name="num_questions"
              value={formData.num_questions}
              onChange={handleChange}
              min="1"
              max="20"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div className="flex justify-end">
            <Button 
              type="button" 
              variant="secondary" 
              className="mr-3"
              onClick={() => navigate(-1)}
              disabled={generating}
            >
              Annuler
            </Button>
            <Button 
              type="submit" 
              variant="primary" 
              disabled={generating}
            >
              {generating ? <LoadingSpinner /> : 'Générer le quiz'}
            </Button>
          </div>
        </form>
      </Card>
      
      {generating && (
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-lg">
          <p className="flex items-center">
            <LoadingSpinner />
            <span className="ml-3">
              Génération de votre quiz en cours... Cela peut prendre quelques instants.
            </span>
          </p>
        </div>
      )}
    </div>
  );
}