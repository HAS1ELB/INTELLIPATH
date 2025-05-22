import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Card from '../components/Card';
import Input from '../components/Input';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const { signUp } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation des mots de passe
    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      setLoading(false);
      return;
    }

    // Validation de la force du mot de passe
    if (password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      setLoading(false);
      return;
    }

    try {
      const { data, error } = await signUp(email, password);
      
      if (error) throw error;
      
      // Si Supabase est configuré pour confirmer les emails
      setSuccess(true);
    } catch (error) {
      console.error('Erreur d\'inscription détaillée:', error);
      // Afficher le message d'erreur spécifique
      setError(`Erreur lors de l'inscription: ${error.message || JSON.stringify(error)}`);
      if (error.message.includes('already registered')) {
        setError('Cet email est déjà utilisé');
      } else {
        setError('Erreur lors de l\'inscription. Veuillez réessayer.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <Card title="Inscription">
        {success ? (
          <div className="text-center">
            <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-md">
              <p>Un email de confirmation a été envoyé à {email}.</p>
              <p>Veuillez vérifier votre boîte de réception et cliquer sur le lien de confirmation pour activer votre compte.</p>
            </div>
            <Link to="/login">
              <Button>Retour à la connexion</Button>
            </Link>
          </div>
        ) : (
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
              autoComplete="new-password"
            />

            <Input
              label="Confirmer le mot de passe"
              type="password"
              name="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
            />

            <Button type="submit" variant="primary" fullWidth disabled={loading}>
              {loading ? <LoadingSpinner /> : 'S\'inscrire'}
            </Button>
          </form>
        )}

        {!success && (
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Vous avez déjà un compte ?{' '}
              <Link to="/login" className="text-blue-600 dark:text-blue-400 hover:underline">
                Se connecter
              </Link>
            </p>
          </div>
        )}
      </Card>
    </div>
  );
}