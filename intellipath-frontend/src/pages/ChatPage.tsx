import { useEffect } from 'react';
import ChatInterface from '../components/ChatInterface';
import { useSession } from '../contexts/SessionContext';
import { Link } from 'react-router-dom';

const ChatPage = () => {
  const { topic, modules } = useSession();

  // Fonction pour le retour en haut de page
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Discussion avec votre instructeur IA</h1>
        <p className="text-gray-600">
          Posez des questions sur le sujet <span className="font-semibold">{topic}</span> à votre instructeur personnalisé
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChatInterface />
        </div>
        
        <div className="lg:col-span-1">
          <div className="card sticky top-6">
            <h2 className="text-xl font-bold mb-4">Suggestions de questions</h2>
            <div className="space-y-2 mb-6">
              <button
                className="w-full text-left p-2 rounded bg-gray-100 hover:bg-gray-200 transition-colors"
                onClick={() => {
                  const textarea = document.querySelector('textarea');
                  if (textarea) {
                    textarea.value = `Pouvez-vous m'expliquer le concept principal de ${topic} ?`;
                    textarea.focus();
                  }
                }}
              >
                Pouvez-vous m'expliquer le concept principal de {topic} ?
              </button>
              
              <button
                className="w-full text-left p-2 rounded bg-gray-100 hover:bg-gray-200 transition-colors"
                onClick={() => {
                  const textarea = document.querySelector('textarea');
                  if (textarea) {
                    textarea.value = "Quelles sont les applications pratiques de ce sujet ?";
                    textarea.focus();
                  }
                }}
              >
                Quelles sont les applications pratiques de ce sujet ?
              </button>
              
              <button
                className="w-full text-left p-2 rounded bg-gray-100 hover:bg-gray-200 transition-colors"
                onClick={() => {
                  const textarea = document.querySelector('textarea');
                  if (textarea) {
                    textarea.value = "Pourriez-vous me donner des exemples concrets ?";
                    textarea.focus();
                  }
                }}
              >
                Pourriez-vous me donner des exemples concrets ?
              </button>
              
              <button
                className="w-full text-left p-2 rounded bg-gray-100 hover:bg-gray-200 transition-colors"
                onClick={() => {
                  const textarea = document.querySelector('textarea');
                  if (textarea) {
                    textarea.value = "Quels sont les défis ou difficultés courants dans ce domaine ?";
                    textarea.focus();
                  }
                }}
              >
                Quels sont les défis ou difficultés courants dans ce domaine ?
              </button>
            </div>
            
            <h3 className="font-semibold mb-2 mt-4">Modules du cours</h3>
            <div className="space-y-2">
              {modules.slice(0, 3).map((module, index) => (
                <div key={index} className="p-2 rounded bg-white border border-gray-200">
                  <h4 className="font-medium">{module.title}</h4>
                  <button
                    className="text-sm text-primary hover:text-primary-dark mt-1"
                    onClick={() => {
                      const textarea = document.querySelector('textarea');
                      if (textarea) {
                        textarea.value = `J'ai des questions sur "${module.title}". Pouvez-vous m'en dire plus ?`;
                        textarea.focus();
                      }
                    }}
                  >
                    Poser une question
                  </button>
                </div>
              ))}
              
              {modules.length > 3 && (
                <Link to="/syllabus" className="text-primary hover:text-primary-dark text-sm block mt-2">
                  Voir tous les modules →
                </Link>
              )}
            </div>
            
            <div className="mt-6 pt-4 border-t border-gray-200">
              <Link to="/quiz" className="btn-secondary w-full text-center block">
                Passer un quiz
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;