import { useState, useRef, useEffect } from 'react';
import { useSession } from '../contexts/SessionContext';
import { sendMessage } from '../services/api';
import { Message } from '../types';
import ReactMarkdown from 'react-markdown';


const ChatInterface = () => {
  const { sessionId, conversationHistory, updateConversationHistory } = useSession();
  const [userMessage, setUserMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [conversationHistory]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setUserMessage(e.target.value);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userMessage.trim() || !sessionId) return;
    setLoading(true);
    setError(null);

    try {
      const response = await sendMessage(sessionId, userMessage);
      updateConversationHistory(response.conversation_history);
      setUserMessage('');
    } catch (err: any) {
      console.error('Erreur lors de l\'envoi du message:', err);
      setError(err.response?.data?.error || 'Une erreur est survenue. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = (message: Message, index: number) => {
    const isUser = message.role === 'user';
    
    return (
      <div 
        key={index}
        className={`mb-4 flex ${isUser ? 'justify-end' : 'justify-start'}`}
      >
        <div 
          className={`rounded-lg px-4 py-2 max-w-[80%] ${
            isUser 
              ? 'bg-primary text-white rounded-br-none' 
              : 'bg-gray-100 text-gray-800 rounded-bl-none'
          }`}
        >
          <ReactMarkdown className="prose prose-sm max-w-none">
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-[calc(100vh-300px)] min-h-[500px]">
      <div className="bg-white rounded-t-lg shadow-md p-4 border-b">
        <h2 className="text-xl font-bold text-gray-800">Conversation avec votre instructeur IA</h2>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 m-2 rounded" role="alert">
          <p>{error}</p>
        </div>
      )}
      
      <div className="flex-grow overflow-y-auto p-4 bg-gray-50 rounded-lg">
        {conversationHistory.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <p className="text-center">
              Commencez à discuter avec votre instructeur IA pour approfondir vos connaissances
              sur le sujet ou poser des questions sur le syllabus.
            </p>
          </div>
        ) : (
          <>
            {conversationHistory.map(renderMessage)}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
      
      <div className="bg-white rounded-b-lg shadow-md p-4 border-t">
        <form onSubmit={handleSendMessage} className="flex items-end space-x-2">
          <div className="flex-grow">
            <textarea
              className="input-field min-h-[80px]"
              placeholder="Posez une question à votre instructeur..."
              value={userMessage}
              onChange={handleInputChange}
              disabled={loading}
              rows={3}
            />
          </div>
          <button
            type="submit"
            className="btn-primary h-10 flex items-center justify-center"
            disabled={loading || !userMessage.trim()}
          >
            {loading ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
              </svg>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;