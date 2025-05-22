import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Card from '../components/Card';
import Input from '../components/Input';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const { error } = await signIn(email, password);
      if (error) throw error;
    } catch (error) {
      console.error('Erreur de connexion:', error);
      setError('Email ou mot de passe incorrect');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <Card title="Connexion">
        <form onSubmit={handleSubmit}>
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md">
              {error}
            </div>
          )}

          <Input
            label="Email"
            type="email"
            name="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />

          <Input
            label="Mot de passe"
            type="password"
            name="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />

          <div className="mb-4 text-right">
            <Link to="/forgot-password" className="text-sm text-blue-600 dark:text-blue-400 hover:underline">
              Mot de passe oublié ?
            </Link>
          </div>

          <Button type="submit" variant="primary" fullWidth disabled={loading}>
            {loading ? <LoadingSpinner /> : 'Se connecter'}
          </Button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Vous n'avez pas de compte ?{' '}
            <Link to="/register" className="text-blue-600 dark:text-blue-400 hover:underline">
              S'inscrire
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
}