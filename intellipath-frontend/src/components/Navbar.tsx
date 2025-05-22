import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useSession } from '../contexts/SessionContext';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { sessionId, topic, clearSession } = useSession();
  const location = useLocation();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const navigation = [
    { name: 'Accueil', path: '/' },
    { name: 'Syllabus', path: '/syllabus', requiresSession: true },
    { name: 'Chat', path: '/chat', requiresSession: true },
    { name: 'Quiz', path: '/quiz', requiresSession: true },
  ];

  return (
    <nav className="bg-primary text-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <span className="text-xl font-bold">IntelliPath</span>
            {topic && (
              <span className="hidden md:inline-block text-sm bg-white/20 px-2 py-1 rounded-md">
                {topic}
              </span>
            )}
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex space-x-6">
            {navigation.map((item) => 
              (!item.requiresSession || sessionId) && (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`hover:text-white/80 ${
                    location.pathname === item.path ? 'font-semibold' : ''
                  }`}
                >
                  {item.name}
                </Link>
              )
            )}
            {sessionId && (
              <button
                onClick={clearSession}
                className="hover:text-white/80"
              >
                Terminer
              </button>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              type="button"
              className="text-white hover:text-white/80"
              onClick={toggleMenu}
            >
              {isMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-white/20">
            <div className="flex flex-col space-y-4">
              {navigation.map((item) => 
                (!item.requiresSession || sessionId) && (
                  <Link
                    key={item.name}
                    to={item.path}
                    className={`hover:text-white/80 ${
                      location.pathname === item.path ? 'font-semibold' : ''
                    }`}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {item.name}
                  </Link>
                )
              )}
              {sessionId && (
                <button
                  onClick={() => {
                    clearSession();
                    setIsMenuOpen(false);
                  }}
                  className="hover:text-white/80 text-left"
                >
                  Terminer
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;