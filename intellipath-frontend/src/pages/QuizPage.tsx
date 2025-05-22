import { useState, useEffect } from 'react';
import { useSession } from '../contexts/SessionContext';
import QuizComponent from '../components/QuizComponent';
import { Link } from 'react-router-dom';

const QuizPage = () => {
  const { modules, quizHistory } = useSession();
  const [selectedModuleIndex, setSelectedModuleIndex] = useState<number | null>(null);
  
  // Récupérer l'index du module sélectionné depuis la page du syllabus
  useEffect(() => {
    const savedModuleIndex = sessionStorage.getItem('selectedModuleIndex');
    if (savedModuleIndex) {
      setSelectedModuleIndex(parseInt(savedModuleIndex));
      // Supprimer l'index sauvegardé après l'avoir utilisé
      sessionStorage.removeItem('selectedModuleIndex');
    }
  }, []);

  // Fonction pour changer le module sélectionné
  const handleModuleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setSelectedModuleIndex(value === 'all' ? null : parseInt(value));
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Quiz d'évaluation</h1>
        <p className="text-gray-600 mb-4">
          Testez vos connaissances et suivez votre progression
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="mb-6">
            <label htmlFor="module-select" className="block mb-2 font-medium">
              Sélectionnez un module pour le quiz :
            </label>
            <select
              id="module-select"
              value={selectedModuleIndex === null ? 'all' : selectedModuleIndex}
              onChange={handleModuleChange}
              className="input-field"
            >
              <option value="all">Tous les modules</option>
              {modules.map((module, index) => (
                <option key={index} value={index}>
                  Module {index + 1}: {module.title}
                </option>
              ))}
            </select>
          </div>

          <QuizComponent moduleIndex={selectedModuleIndex} />
        </div>
        
        <div className="lg:col-span-1">
          <div className="card mb-6">
            <h2 className="text-xl font-bold mb-4">Historique des quiz</h2>
            
            {quizHistory.length === 0 ? (
              <div className="text-center py-4 text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto mb-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p>Aucun quiz complété pour le moment</p>
              </div>
            ) : (
              <div className="space-y-3">
                {quizHistory.map((item, index) => (
                  <div key={index} className="border rounded-lg p-3 flex items-center">
                    <div className={`h-12 w-12 rounded-full flex items-center justify-center text-white font-bold mr-3 ${
                      item.score >= 70 
                        ? 'bg-green-500' 
                        : item.score >= 40 
                          ? 'bg-amber-500' 
                          : 'bg-red-500'
                    }`}>
                      {Math.round(item.score)}%
                    </div>
                    <div className="flex-grow">
                      <h3 className="font-medium">{item.module}</h3>
                      <div className="flex justify-between text-sm text-gray-500">
                        <span>Difficulté: {item.difficulty}</span>
                        <span>{item.date}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Ressources d'étude</h2>
            <div className="space-y-3">
              <Link to="/syllabus" className="block p-3 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors">
                <div className="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-primary" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                  </svg>
                  <span>Revoir le syllabus complet</span>
                </div>
              </Link>
              
              <Link to="/chat" className="block p-3 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors">
                <div className="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-primary" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                  </svg>
                  <span>Poser des questions à l'instructeur</span>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizPage;