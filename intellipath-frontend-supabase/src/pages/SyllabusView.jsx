import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import ReactMarkdown from 'react-markdown';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function SyllabusView() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [syllabus, setSyllabus] = useState(null);
  const [modules, setModules] = useState([]);
  const [progress, setProgress] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchSyllabusData = async () => {
      try {
        setLoading(true);
        
        // Récupération du syllabus
        const syllabusData = await api.syllabus.getById(id);
        setSyllabus(syllabusData);
        
        // Récupération des modules
        const modulesData = await api.modules.getModulesBySyllabusId(id);
        setModules(modulesData);
        
        // Création ou récupération d'une session
        try {
          // On essaie de créer une nouvelle session
          // Dans un système complet, vous stockeriez les sessions dans Supabase et les récupéreriez
          const sessionResponse = await api.session.getSession(id);
          setSessionId(sessionResponse.session_id);
          
          // Récupération des données de progression
          if (sessionResponse.progress) {
            setProgress(sessionResponse.progress);
          }
        } catch (sessionError) {
          console.error('Erreur de session, création d\'une nouvelle session:', sessionError);
          // Dans un système réel, nous créerions une nouvelle session ici
          setSessionId(id); // Utiliser l'ID du syllabus comme ID de session temporaire
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des données du syllabus:', error);
        setError('Impossible de charger les données du syllabus');
      } finally {
        setLoading(false);
      }
    };

    fetchSyllabusData();
  }, [id]);

  // Fonction pour obtenir le pourcentage de progression pour un module donné
  const getModuleProgress = (moduleId) => {
    if (!progress || progress.length === 0) return 0;
    
    const moduleProgress = progress.find(p => p.module_id === moduleId);
    return moduleProgress ? moduleProgress.completion_percentage : 0;
  };

  // Fonction pour obtenir le statut d'un module
  const getModuleStatus = (moduleId) => {
    if (!progress || progress.length === 0) return 'not_started';
    
    const moduleProgress = progress.find(p => p.module_id === moduleId);
    return moduleProgress ? moduleProgress.status : 'not_started';
  };

  // Fonction pour formater la date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('fr-FR', options);
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

  if (!syllabus) {
    return (
      <div className="text-center">
        <h2 className="text-xl font-medium mb-4 text-gray-900 dark:text-white">Syllabus non trouvé</h2>
        <p className="mb-4">Le syllabus que vous recherchez n'existe pas ou a été supprimé.</p>
        <Button onClick={() => navigate('/dashboard')}>Retour au tableau de bord</Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {syllabus.topic}
          </h1>
          <div className="flex space-x-2">
            <Link to={`/chat/${sessionId}`}>
              <Button variant="secondary">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1 inline-block" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                </svg>
                Discuter avec l'agent
              </Button>
            </Link>
            <Link to={`/quiz/create/${sessionId}`}>
              <Button variant="primary">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1 inline-block" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M9 3a1 1 0 012 0v5.5a.5.5 0 001 0V4a1 1 0 112 0v4.5a.5.5 0 001 0V6a1 1 0 112 0v5a7 7 0 11-14 0V9a1 1 0 012 0v2.5a.5.5 0 001 0V4a1 1 0 012 0v4.5a.5.5 0 001 0V3z" clipRule="evenodd" />
                </svg>
                Générer un quiz
              </Button>
            </Link>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-3 mt-2 text-sm text-gray-500 dark:text-gray-400">
          <span>Niveau: {syllabus.level}</span>
          <span>•</span>
          <span>Durée: {syllabus.duration}</span>
          <span>•</span>
          <span>Style: {syllabus.learning_style}</span>
          <span>•</span>
          <span>Créé le {formatDate(syllabus.created_at)}</span>
        </div>
      </div>

      {/* Description globale du syllabus */}
      <Card className="mb-6">
        <div className="prose dark:prose-invert prose-blue max-w-none">
          <ReactMarkdown>{syllabus.content}</ReactMarkdown>
        </div>
      </Card>

      {/* Liste des modules */}
      <h2 className="text-xl font-medium mb-4 text-gray-900 dark:text-white">Modules</h2>
      <div className="space-y-4">
        {modules.map((module, index) => {
          const progress = getModuleProgress(module.id);
          const status = getModuleStatus(module.id);
          
          let statusBadge;
          if (status === 'completed') {
            statusBadge = <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 rounded-full">Complété</span>;
          } else if (status === 'in_progress') {
            statusBadge = <span className="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400 rounded-full">En cours</span>;
          } else {
            statusBadge = <span className="ml-2 px-2 py-1 text-xs bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400 rounded-full">À commencer</span>;
          }
          
          return (
            <Card key={module.id} className="hover:shadow-lg transition-shadow duration-200">
              <div>
                <div className="flex justify-between items-start">
                  <h3 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">
                    {index + 1}. {module.title} {statusBadge}
                  </h3>
                </div>
                
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                  {module.description || "Aucune description disponible"}
                </p>
                
                {/* Barre de progression */}
                <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full mb-3">
                  <div
                    className="h-full bg-blue-600 rounded-full"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {Math.round(progress)}% terminé
                  </span>
                  <Link to={`/module/${module.id}`}>
                    <Button size="sm" variant="outline">
                      {status === 'not_started' ? 'Commencer' : 'Continuer'}
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}