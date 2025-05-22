import { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import ReactMarkdown from 'react-markdown';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function ChatView() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  
  const [syllabus, setSyllabus] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const fetchChatData = async () => {
      try {
        setLoading(true);
        
        // Dans un système réel, vous récupéreriez la session et son historique
        // Pour l'exemple, nous allons essayer de récupérer les données de session
        try {
          const sessionData = await api.session.getSession(sessionId);
          
          if (sessionData.syllabus) {
            setSyllabus(sessionData.syllabus);
          }
          
          if (sessionData.conversation_history) {
            setMessages(sessionData.conversation_history);
          } else {
            // Ajouter un message de bienvenue par défaut
            setMessages([
              {
                role: 'assistant',
                content: `Bonjour, je suis votre assistant d'apprentissage. Je suis là pour vous aider dans votre parcours sur "${sessionData.topic || 'ce sujet'}". Comment puis-je vous aider aujourd'hui ?`
              }
            ]);
          }
        } catch (error) {
          console.error('Erreur lors de la récupération de la session:', error);
          // Message de bienvenue par défaut en cas d'erreur
          setMessages([
            {
              role: 'assistant',
              content: "Bonjour, je suis votre assistant d'apprentissage. Comment puis-je vous aider aujourd'hui ?"
            }
          ]);
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des données de chat:', error);
        setError('Impossible de charger la conversation. Veuillez réessayer.');
      } finally {
        setLoading(false);
      }
    };

    fetchChatData();
  }, [sessionId]);

  // Défilement automatique vers le dernier message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim()) return;
    
    const userMessage = {
      role: 'user',
      content: newMessage
    };
    
    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setSending(true);
    
    try {
      // Appel à l'API pour envoyer le message à l'agent
      const response = await api.conversation.sendMessage(sessionId, newMessage);
      
      if (response.response) {
        const assistantMessage = {
          role: 'assistant',
          content: response.response
        };
        
        // Mettre à jour avec tous les messages, y compris l'historique complet si disponible
        if (response.conversation_history) {
          setMessages(response.conversation_history);
        } else {
          setMessages(prev => [...prev, assistantMessage]);
        }
      }
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      setError('Erreur lors de l\'envoi du message. Veuillez réessayer.');
      
      // Ajouter un message d'erreur
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Désolé, une erreur s\'est produite. Veuillez réessayer.'
      }]);
    } finally {
      setSending(false);
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
    <div className="max-w-4xl mx-auto">
      {/* En-tête */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <Link 
            to={syllabus ? `/syllabus/${syllabus.id}` : '/dashboard'}
            className="text-blue-600 dark:text-blue-400 hover:underline flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            {syllabus ? 'Retour au syllabus' : 'Retour au tableau de bord'}
          </Link>
          <h1 className="text-2xl font-bold mt-2 text-gray-900 dark:text-white">
            Discussion avec l'assistant
          </h1>
          {syllabus && (
            <p className="text-gray-600 dark:text-gray-400">
              {syllabus.topic}
            </p>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md">
          {error}
        </div>
      )}

      {/* Zone de chat */}
      <Card className="mb-6 p-0 overflow-hidden">
        <div className="h-[60vh] overflow-y-auto p-6">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`mb-4 flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                }`}
              >
                <div className="prose dark:prose-invert prose-sm max-w-none">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Formulaire de saisie */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Tapez votre message ici..."
              className="flex-grow px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
              disabled={sending}
            />
            <Button
              type="submit"
              disabled={sending || !newMessage.trim()}
            >
              {sending ? (
                <LoadingSpinner />
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              )}
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}