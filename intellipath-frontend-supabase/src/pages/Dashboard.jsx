import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Dashboard() {
  const { user } = useAuth();
  const [syllabi, setSyllabi] = useState([]);
  const [progressData, setProgressData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setLoading(true);
        
        // Récupération des syllabus de l'utilisateur
        const userSyllabi = await api.syllabus.getUserSyllabi();
        setSyllabi(userSyllabi || []);
        
        // Récupération des données de progression
        const progressResponse = await api.progress.getUserProgress();
        setProgressData(progressResponse.progress || []);
      } catch (error) {
        console.error('Erreur lors de la récupération des données utilisateur:', error);
        setError('Impossible de charger vos données. Veuillez réessayer.');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [user]);

  // Fonction pour obtenir le pourcentage de progression pour un syllabus donné
  const getSyllabusProgress = (syllabusId) => {
    const progress = progressData.find(p => p.syllabus_id === syllabusId);
    return progress ? progress.completion_percentage : 0;
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

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Tableau de bord</h1>
        <Link to="/syllabus/create">
          <Button>Créer un nouveau syllabus</Button>
        </Link>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg">
          {error}
        </div>
      )}

      {syllabi.length === 0 ? (
        <Card className="text-center py-8">
          <div className="text-gray-500 dark:text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <h3 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">Vous n'avez pas encore de syllabus</h3>
            <p className="mb-4">Commencez par créer votre premier parcours d'apprentissage</p>
            <Link to="/syllabus/create">
              <Button>Créer un syllabus</Button>
            </Link>
          </div>
        </Card>
      ) : (
        <div>
          <h2 className="text-xl font-medium mb-4 text-gray-900 dark:text-white">Mes parcours d'apprentissage</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {syllabi.map((syllabus) => {
              const progress = getSyllabusProgress(syllabus.id);
              return (
                <Card key={syllabus.id} className="h-full flex flex-col">
                  <div className="flex-grow">
                    <h3 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">
                      {syllabus.topic}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                      Niveau: {syllabus.level} · Durée: {syllabus.duration}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                      Créé le {formatDate(syllabus.created_at)}
                    </p>
                    
                    {/* Barre de progression */}
                    <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full mb-2">
                      <div
                        className="h-full bg-blue-600 rounded-full"
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      {Math.round(progress)}% terminé
                    </p>
                  </div>
                  
                  <div className="mt-4">
                    <Link to={`/syllabus/${syllabus.id}`}>
                      <Button variant="primary" fullWidth>
                        Continuer
                      </Button>
                    </Link>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}