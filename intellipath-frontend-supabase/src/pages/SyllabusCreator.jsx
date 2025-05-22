import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import Card from '../components/Card';
import Input from '../components/Input';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function SyllabusCreator() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    topic: '',
    level: 'Intermédiaire',
    duration: '1 mois',
    learning_style: 'Pratique',
    include_projects: true,
    include_resources: true,
    include_assessments: true,
    temperature: 0.7
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Valider le formulaire
    if (!formData.topic.trim()) {
      setError('Le sujet est requis');
      setLoading(false);
      return;
    }

    try {
      // Appeler l'API pour créer le syllabus
      const response = await api.syllabus.create(formData);
      
      // Rediriger vers la page du syllabus créé
      navigate(`/syllabus/${response.syllabus.id}`);
    } catch (error) {
      console.error('Erreur lors de la création du syllabus:', error);
      setError('Une erreur est survenue lors de la création du syllabus');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card title="Créer un nouveau parcours d'apprentissage">
        {error && (
          <div className="mb-6 p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <Input
            label="Sujet"
            name="topic"
            value={formData.topic}
            onChange={handleChange}
            placeholder="Ex: Développement web, Machine Learning, Marketing digital..."
            required
          />

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Niveau
            </label>
            <select
              name="level"
              value={formData.level}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="Débutant">Débutant</option>
              <option value="Intermédiaire">Intermédiaire</option>
              <option value="Avancé">Avancé</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Durée estimée
            </label>
            <select
              name="duration"
              value={formData.duration}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="1 semaine">1 semaine</option>
              <option value="2 semaines">2 semaines</option>
              <option value="1 mois">1 mois</option>
              <option value="3 mois">3 mois</option>
              <option value="6 mois">6 mois</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Style d'apprentissage
            </label>
            <select
              name="learning_style"
              value={formData.learning_style}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="Théorique">Théorique</option>
              <option value="Pratique">Pratique</option>
              <option value="Visuel">Visuel</option>
              <option value="Auditif">Auditif</option>
              <option value="Lecture/Écriture">Lecture/Écriture</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                name="include_projects"
                checked={formData.include_projects}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Inclure des projets pratiques
              </span>
            </label>
          </div>

          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                name="include_resources"
                checked={formData.include_resources}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Inclure des ressources d'apprentissage (livres, articles, vidéos...)
              </span>
            </label>
          </div>

          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                name="include_assessments"
                checked={formData.include_assessments}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Inclure des évaluations progressives
              </span>
            </label>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Créativité (0.1 = conservateur, 1.0 = créatif)
            </label>
            <input
              type="range"
              name="temperature"
              min="0.1"
              max="1"
              step="0.1"
              value={formData.temperature}
              onChange={handleChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>0.1</span>
              <span>0.5</span>
              <span>1.0</span>
            </div>
          </div>

          <div className="flex justify-end">
            <Button 
              type="button" 
              variant="secondary" 
              className="mr-3"
              onClick={() => navigate('/dashboard')}
              disabled={loading}
            >
              Annuler
            </Button>
            <Button 
              type="submit" 
              variant="primary" 
              disabled={loading}
            >
              {loading ? <LoadingSpinner /> : 'Créer le syllabus'}
            </Button>
          </div>
        </form>
      </Card>
      
      {loading && (
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-lg">
          <p className="flex items-center">
            <LoadingSpinner />
            <span className="ml-3">
              Génération de votre syllabus en cours... Cela peut prendre quelques instants.
            </span>
          </p>
        </div>
      )}
    </div>
  );
}