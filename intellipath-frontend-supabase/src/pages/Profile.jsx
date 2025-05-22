import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabaseClient';
import { api } from '../services/api';
import Card from '../components/Card';
import Input from '../components/Input';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Profile() {
  const { user, updateProfile } = useAuth();
  
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: ''
  });
  const [progressData, setProgressData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setLoading(true);
        
        // Récupérer les données du profil
        const { data, error } = await supabase
          .from('users')
          .select('*')
          .eq('id', user.id)
          .single();
        
        if (error) throw error;
        
        if (data) {
          setFormData({
            first_name: data.first_name || '',
            last_name: data.last_name || '',
            email: user.email || ''
          });
        }
        
        // Récupérer les données de progression
        try {
          const progressResponse = await api.progress.getUserProgress();
          setProgressData(progressResponse.progress || []);
        } catch (progressError) {
          console.error('Erreur lors de la récupération de la progression:', progressError);
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des données utilisateur:', error);
        setError('Impossible de charger les données du profil');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchUserData();
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUpdating(true);
    setError('');
    setSuccess('');

    try {
      const { data, error } = await updateProfile({
        first_name: formData.first_name,
        last_name: formData.last_name,
        updated_at: new Date()
      });
      
      if (error) throw error;
      
      setSuccess('Profil mis à jour avec succès');
    } catch (error) {
      console.error('Erreur lors de la mise à jour du profil:', error);
      setError('Erreur lors de la mise à jour du profil');
    } finally {
      setUpdating(false);
    }
  };

  // Fonction pour formater la date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('fr-FR', options);
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
      <h1 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Mon profil</h1>
      
      <div className="grid md:grid-cols-3 gap-6">
        {/* Profil utilisateur */}
        <div className="md:col-span-2">
          <Card title="Informations personnelles">
            {error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md">
                {error}
              </div>
            )}
            
            {success && (
              <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-md">
                {success}
              </div>
            )}
            
            <form onSubmit={handleSubmit}>
              <Input
                label="Email"
                type="email"
                name="email"
                value={formData.email}
                disabled
              />
              
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Prénom"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                />
                
                <Input
                  label="Nom"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                />
              </div>
              
              <div className="mt-6 text-right">
                <Button
                  type="submit"
                  disabled={updating}
                >
                  {updating ? <LoadingSpinner /> : 'Enregistrer'}
                </Button>
              </div>
            </form>
          </Card>
          
          {/* Section pour la sécurité du compte */}
          <Card title="Sécurité du compte" className="mt-6">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Vous pouvez modifier le mot de passe de votre compte ou gérer vos options de sécurité ici.
            </p>
            
            <div className="mt-4">
              <Button 
                variant="outline"
                onClick={() => alert('Fonctionnalité non implémentée dans cette démo')}
              >
                Changer de mot de passe
              </Button>
            </div>
          </Card>
        </div>
        
        {/* Statistiques et progression */}
        <div>
          <Card title="Mes statistiques">
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Parcours d'apprentissage</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{progressData.length}</p>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Parcours complétés</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {progressData.filter(p => p.status === 'completed').length}
                </p>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Progression moyenne</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {progressData.length 
                    ? Math.round(progressData.reduce((acc, curr) => acc + curr.completion_percentage, 0) / progressData.length)
                    : 0}%
                </p>
              </div>
              
              {user && (
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Membre depuis</p>
                  <p className="text-lg font-medium text-gray-900 dark:text-white">
                    {formatDate(user.created_at || new Date())}
                  </p>
                </div>
              )}
            </div>
          </Card>
          
          {progressData.length > 0 && (
            <Card title="Dernières activités" className="mt-6">
              <div className="space-y-4">
                {progressData
                  .sort((a, b) => new Date(b.last_activity_at) - new Date(a.last_activity_at))
                  .slice(0, 3)
                  .map((progress, index) => (
                    <div key={index} className="border-b border-gray-200 dark:border-gray-700 pb-2 last:border-0 last:pb-0">
                      <p className="font-medium text-gray-900 dark:text-white">{progress.topic}</p>
                      <div className="flex justify-between items-center mt-1">
                        <div className="w-2/3">
                          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                            <div
                              className="h-full bg-blue-600 rounded-full"
                              style={{ width: `${progress.completion_percentage}%` }}
                            ></div>
                          </div>
                        </div>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {Math.round(progress.completion_percentage)}%
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Dernière activité: {formatDate(progress.last_activity_at)}
                      </p>
                    </div>
                  ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}