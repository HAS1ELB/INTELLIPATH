import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/Button';

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="flex flex-col items-center">
      <div className="text-center max-w-3xl">
        <h1 className="text-4xl font-bold mb-6 text-blue-600 dark:text-blue-400">
          Bienvenue sur IntelliPath
        </h1>
        <p className="text-xl mb-8 text-gray-700 dark:text-gray-300">
          Une plateforme d'apprentissage personnalisée qui s'adapte à votre style d'apprentissage et à vos objectifs.
        </p>
        <div className="mb-12">
          {user ? (
            <Link to="/dashboard">
              <Button size="lg">
                Accéder à mon tableau de bord
              </Button>
            </Link>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register">
                <Button size="lg">
                  Commencer gratuitement
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="outline">
                  Se connecter
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Section caractéristiques */}
      <div className="grid md:grid-cols-3 gap-8 w-full max-w-5xl mt-8">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <div className="text-blue-600 dark:text-blue-400 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Apprentissage personnalisé</h3>
          <p className="text-gray-600 dark:text-gray-400">
            Des parcours adaptés à votre niveau, votre style d'apprentissage et vos objectifs.
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <div className="text-blue-600 dark:text-blue-400 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Assistant IA</h3>
          <p className="text-gray-600 dark:text-gray-400">
            Un tuteur virtuel disponible 24/7 pour répondre à vos questions et vous guider.
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <div className="text-blue-600 dark:text-blue-400 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Suivi de progression</h3>
          <p className="text-gray-600 dark:text-gray-400">
            Suivez votre évolution et identifiez vos points forts et vos axes d'amélioration.
          </p>
        </div>
      </div>

      {/* Section témoignages */}
      <div className="mt-16 w-full max-w-5xl">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-900 dark:text-white">Ce que nos utilisateurs disent</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              "IntelliPath m'a permis d'apprendre à mon rythme et selon ma méthode d'apprentissage préférée. Le tuteur IA est incroyablement utile!"
            </p>
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-200 rounded-full flex items-center justify-center text-blue-600">
                SL
              </div>
              <div className="ml-3">
                <p className="text-gray-900 dark:text-white font-medium">Sophie L.</p>
                <p className="text-gray-500 dark:text-gray-400 text-sm">Étudiante en informatique</p>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              "J'ai pu créer un parcours d'apprentissage complet en développement web et suivre ma progression. Les quiz générés sont particulièrement pertinents."
            </p>
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-200 rounded-full flex items-center justify-center text-blue-600">
                TM
              </div>
              <div className="ml-3">
                <p className="text-gray-900 dark:text-white font-medium">Thomas M.</p>
                <p className="text-gray-500 dark:text-gray-400 text-sm">Développeur en reconversion</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Appel à l'action */}
      <div className="mt-16 mb-8 text-center">
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Prêt à commencer votre parcours d'apprentissage ?</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-2xl mx-auto">
          Rejoignez IntelliPath aujourd'hui et découvrez une nouvelle façon d'apprendre, adaptée à vos besoins et à votre style.
        </p>
        {!user && (
          <Link to="/register">
            <Button size="lg">
              S'inscrire gratuitement
            </Button>
          </Link>
        )}
      </div>
    </div>
  );
}