import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createSyllabus } from '../services/api';
import { useSession } from '../contexts/SessionContext';
import { SyllabusFormData } from '../types';

const SyllabusForm = () => {
  const navigate = useNavigate();
  const { setSyllabusData } = useSession();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<SyllabusFormData>({
    topic: '',
    level: 'Intermédiaire',
    duration: '1 mois',
    learning_style: 'Pratique',
    include_projects: true,
    include_resources: true,
    include_assessments: true,
    temperature: 0.7,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checkbox = e.target as HTMLInputElement;
      setFormData({
        ...formData,
        [name]: checkbox.checked,
      });
    } else if (name === 'temperature') {
      setFormData({
        ...formData,
        temperature: parseFloat(value),
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await createSyllabus(formData);
      setSyllabusData(data);
      navigate('/syllabus');
    } catch (err: any) {
      console.error('Erreur lors de la création du syllabus:', err);
      setError(err.response?.data?.error || 'Une erreur est survenue. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-center">Créer votre parcours d'apprentissage</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
          <p>{error}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="topic" className="block mb-2 font-medium">
            Sujet d'apprentissage <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="topic"
            name="topic"
            value={formData.topic}
            onChange={handleChange}
            className="input-field"
            placeholder="Ex: Python, Marketing Digital, Intelligence Artificielle..."
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="level" className="block mb-2 font-medium">
              Niveau
            </label>
            <select
              id="level"
              name="level"
              value={formData.level}
              onChange={handleChange}
              className="input-field"
            >
              <option value="Débutant">Débutant</option>
              <option value="Intermédiaire">Intermédiaire</option>
              <option value="Avancé">Avancé</option>
            </select>
          </div>

          <div>
            <label htmlFor="duration" className="block mb-2 font-medium">
              Durée
            </label>
            <input
              type="text"
              id="duration"
              name="duration"
              value={formData.duration}
              onChange={handleChange}
              className="input-field"
              placeholder="Ex: 2 semaines, 1 mois, 3 mois..."
            />
          </div>
        </div>

        <div className="mb-4">
          <label htmlFor="learning_style" className="block mb-2 font-medium">
            Style d'apprentissage
          </label>
          <select
            id="learning_style"
            name="learning_style"
            value={formData.learning_style}
            onChange={handleChange}
            className="input-field"
          >
            <option value="Pratique">Pratique</option>
            <option value="Théorique">Théorique</option>
            <option value="Visuel">Visuel</option>
            <option value="Auditif">Auditif</option>
          </select>
        </div>

        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="include_projects"
              name="include_projects"
              checked={formData.include_projects}
              onChange={handleChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            />
            <label htmlFor="include_projects" className="ml-2 text-sm">
              Inclure des projets
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="include_resources"
              name="include_resources"
              checked={formData.include_resources}
              onChange={handleChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            />
            <label htmlFor="include_resources" className="ml-2 text-sm">
              Inclure des ressources
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="include_assessments"
              name="include_assessments"
              checked={formData.include_assessments}
              onChange={handleChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            />
            <label htmlFor="include_assessments" className="ml-2 text-sm">
              Inclure des évaluations
            </label>
          </div>
        </div>

        <div className="mb-6">
          <label htmlFor="temperature" className="block mb-2 font-medium">
            Créativité (température): {formData.temperature}
          </label>
          <input
            type="range"
            id="temperature"
            name="temperature"
            min="0.1"
            max="1"
            step="0.1"
            value={formData.temperature}
            onChange={handleChange}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Structuré</span>
            <span>Créatif</span>
          </div>
        </div>

        <div className="flex justify-center">
          <button
            type="submit"
            className="btn-primary w-full md:w-auto"
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
              'Créer mon parcours'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SyllabusForm;