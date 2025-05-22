import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import ReactMarkdown from 'react-markdown';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function ModuleView() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [module, setModule] = useState(null);
  const [syllabus, setSyllabus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isCompleting, setIsCompleting] = useState(false);

  useEffect(() => {
    const fetchModuleData = async () => {
      try {
        setLoading(true);
        
        // Récupération du module
        const moduleData = await api.modules.getById(id);
        setModule(moduleData);
        
        // Récupération du syllabus parent
        if (moduleData.syllabus_id) {
          const syllabusData = await api.syllabus.getById(moduleData.syllabus_id);
          setSyllabus(syllabusData);
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des données du module:', error);
        setError('Impossible de charger les données du module');
      } finally {
        setLoading(false);
      }
    };

    fetchModuleData();
  }, [id]);

  const handleCompleteModule = async () => {
    try {
      setIsCompleting(true);
      await api.modules.completeModule(id);
      
      // Actualiser les données du module pour refléter la complétion
      const moduleData = await api.modules.getById(id);
      setModule(moduleData);
      
      setTimeout(() => {
        // Rediriger vers le syllabus après un court délai
        navigate(`/syllabus/${module.syllabus_id}`);
      }, 1500);
    } catch (error) {
      console.error('Erreur lors de la complétion du module:', error);
      setError('Erreur lors de la complétion du module');
    } finally {
      setIsCompleting(false);
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
      </div>
    );
  }

  if (!module) {
    return (
      <div className="text-center">
        <h2 className="text-xl font-medium mb-4 text-gray-900 dark:text-white">Module non trouvé</h2>
        <p className="mb-4">Le module que vous recherchez n'existe pas ou a été supprimé.</p>
        <Button onClick={() => navigate('/dashboard')}>Retour au tableau de bord</Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Barre de navigation du module */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <Link 
            to={`/syllabus/${module.syllabus_id}`}
            className="text-blue-600 dark:text-blue-400 hover:underline flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            Retour au syllabus
          </Link>
          <h1 className="text-2xl font-bold mt-2 text-gray-900 dark:text-white">
            {module.title}
          </h1>
          {syllabus && (
            <p className="text-gray-600 dark:text-gray-400">
              {syllabus.topic}
            </p>
          )}
        </div>
        
        <div className="flex space-x-2">
          <Link to={`/chat/${module.syllabus_id}`}>
            <Button variant="secondary">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1 inline-block" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
              </svg>
              Discuter
            </Button>
          </Link>
          <Link to={`/quiz/create/${module.syllabus_id}?module=${id}`}>
            <Button variant="outline">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1 inline-block" viewBox="0 0 20 20" fill="currentColor">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
              </svg>
              Quiz
            </Button>
          </Link>
        </div>
      </div>

      {/* Contenu du module */}
      <Card className="mb-6">
        {module.content ? (
          <div className="prose dark:prose-invert prose-blue max-w-none">
            <ReactMarkdown>{module.content}</ReactMarkdown>
          </div>
        ) : (
          <div className="text-center text-gray-500 dark:text-gray-400 py-8">
            <p>Le contenu détaillé de ce module n'est pas disponible.</p>
            <p>Essayez de discuter avec l'agent d'enseignement pour en savoir plus.</p>
          </div>
        )}
      </Card>

      {/* Bouton de complétion */}
      <div className="flex justify-center">
        <Button
          variant="primary"
          size="lg"
          onClick={handleCompleteModule}
          disabled={isCompleting}
        >
          {isCompleting ? (
            <>
              <LoadingSpinner /> 
              <span className="ml-2">Validation en cours...</span>
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Marquer comme terminé
            </>
          )}
        </Button>
      </div>
    </div>
  );
}