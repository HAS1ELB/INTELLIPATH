import React from 'react';
import { useSession } from '../contexts/SessionContext';
import { useNavigate } from 'react-router-dom';
import SyllabusForm from '../components/SyllabusForm';

const HomePage: React.FC = () => {
  const { sessionId, topic } = useSession();
  const navigate = useNavigate();

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
          Bienvenue sur <span className="text-primary">IntelliPath</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Votre assistant d'apprentissage personnalisé propulsé par l'intelligence artificielle
        </p>
      </div>

      {sessionId ? (
        <div className="text-center mb-12 p-6 bg-white rounded-xl shadow-md">
          <h2 className="text-2xl font-semibold mb-4">
            Vous avez un parcours d'apprentissage actif
          </h2>
          <p className="text-lg mb-6">
            Vous êtes actuellement en train d'apprendre <span className="font-semibold text-primary">{topic}</span>
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => navigate('/syllabus')}
              className="p-4 rounded-lg bg-primary-light hover:bg-primary text-white transition-colors flex flex-col items-center justify-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              Voir Syllabus
            </button>
            <button
              onClick={() => navigate('/chat')}
              className="p-4 rounded-lg bg-secondary-light hover:bg-secondary text-white transition-colors flex flex-col items-center justify-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              Discuter
            </button>
            <button
              onClick={() => navigate('/quiz')}
              className="p-4 rounded-lg bg-amber-500 hover:bg-amber-600 text-white transition-colors flex flex-col items-center justify-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Quiz
            </button>
          </div>
        </div>
      ) : (
        <SyllabusForm />
      )}

      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="card text-center">
          <div className="bg-primary-light rounded-full p-4 inline-flex mx-auto mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <h3 className="text-xl font-bold mb-2">Plan Personnalisé</h3>
          <p className="text-gray-600">
            Créez un parcours d'apprentissage adapté à votre niveau, vos objectifs et votre style d'apprentissage.
          </p>
        </div>

        <div className="card text-center">
          <div className="bg-secondary-light rounded-full p-4 inline-flex mx-auto mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold mb-2">Assistant Intelligent</h3>
          <p className="text-gray-600">
            Discutez avec votre tuteur IA personnel qui répond à vos questions et vous guide dans votre apprentissage.
          </p>
        </div>

        <div className="card text-center">
          <div className="bg-amber-500 rounded-full p-4 inline-flex mx-auto mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold mb-2">Évaluations Adaptatives</h3>
          <p className="text-gray-600">
            Testez vos connaissances avec des quiz générés dynamiquement et recevez des retours détaillés.
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;