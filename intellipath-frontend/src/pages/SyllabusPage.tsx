import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../contexts/SessionContext';
import ModuleCard from '../components/ModuleCard';
import ReactMarkdown from 'react-markdown';

const SyllabusPage = () => {
  const { syllabus, modules, topic } = useSession();
  const navigate = useNavigate();
  const [showFullSyllabus, setShowFullSyllabus] = useState(false);

  if (!syllabus || !modules.length) {
    return (
      <div className="text-center p-8">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
        <p className="text-gray-600">Chargement du syllabus...</p>
      </div>
    );
  }

  const handleQuizClick = (moduleIndex: number) => {
    // Stocker l'index du module sélectionné dans sessionStorage
    sessionStorage.setItem('selectedModuleIndex', moduleIndex.toString());
    navigate('/quiz');
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Syllabus: {topic}</h1>
        <p className="text-gray-600 mb-4">
          Votre parcours d'apprentissage personnalisé avec {modules.length} modules
        </p>
        
        <div className="flex flex-wrap gap-3 mb-6">
          <button
            onClick={() => navigate('/chat')}
            className="btn-primary flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
            </svg>
            Discuter avec l'instructeur
          </button>
          
          <button
            onClick={() => navigate('/quiz')}
            className="btn-secondary flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
              <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
            </svg>
            Passer un quiz
          </button>
          
          <button
            onClick={() => setShowFullSyllabus(!showFullSyllabus)}
            className="text-primary hover:text-primary-dark flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              {showFullSyllabus ? (
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              ) : (
                <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
              )}
            </svg>
            {showFullSyllabus ? "Masquer le syllabus complet" : "Afficher le syllabus complet"}
          </button>
        </div>
        
        {showFullSyllabus && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8 prose prose-primary max-w-none">
            <ReactMarkdown>
              {syllabus}
            </ReactMarkdown>
          </div>
        )}
      </div>
      
      <h2 className="text-2xl font-bold mb-4">Modules du cours</h2>
      <div className="space-y-6">
        {modules.map((module, index) => (
          <ModuleCard
            key={index}
            module={module}
            index={index}
            onQuizClick={handleQuizClick}
          />
        ))}
      </div>
    </div>
  );
};

export default SyllabusPage;