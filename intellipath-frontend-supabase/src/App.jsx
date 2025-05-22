import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { Suspense, lazy } from 'react';
import Navbar from './components/Navbar';
import LoadingSpinner from './components/LoadingSpinner';

// Chargement paresseux des composants pour optimiser les performances
const Home = lazy(() => import('./pages/Home'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const SyllabusCreator = lazy(() => import('./pages/SyllabusCreator'));
const SyllabusView = lazy(() => import('./pages/SyllabusView'));
const ModuleView = lazy(() => import('./pages/ModuleView'));
const QuizCreator = lazy(() => import('./pages/QuizCreator'));
const QuizView = lazy(() => import('./pages/QuizView'));
const ChatView = lazy(() => import('./pages/ChatView'));
const Profile = lazy(() => import('./pages/Profile'));

// Route protégée qui redirige vers la connexion si l'utilisateur n'est pas authentifié
function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

function App() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="container py-8">
        <Suspense fallback={<div className="flex justify-center items-center h-[60vh]"><LoadingSpinner /></div>}>
          <Routes>
            {/* Routes publiques */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" replace />} />
            <Route path="/register" element={!user ? <Register /> : <Navigate to="/dashboard" replace />} />
            
            {/* Routes protégées */}
            <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
            <Route path="/syllabus/create" element={<PrivateRoute><SyllabusCreator /></PrivateRoute>} />
            <Route path="/syllabus/:id" element={<PrivateRoute><SyllabusView /></PrivateRoute>} />
            <Route path="/module/:id" element={<PrivateRoute><ModuleView /></PrivateRoute>} />
            <Route path="/quiz/create/:sessionId" element={<PrivateRoute><QuizCreator /></PrivateRoute>} />
            <Route path="/quiz/:id" element={<PrivateRoute><QuizView /></PrivateRoute>} />
            <Route path="/chat/:sessionId" element={<PrivateRoute><ChatView /></PrivateRoute>} />
            
            {/* Route 404 */}
            <Route path="*" element={<div className="text-center"><h1 className="text-3xl font-bold mb-4">Page non trouvée</h1><p>La page que vous recherchez n'existe pas.</p></div>} />
          </Routes>
        </Suspense>
      </main>
      <footer className="py-6 text-center text-gray-500 dark:text-gray-400">
        <p>© {new Date().getFullYear()} IntelliPath - Tous droits réservés</p>
      </footer>
    </div>
  );
}

export default App;