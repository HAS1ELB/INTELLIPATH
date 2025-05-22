const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-gray-800 text-white py-6 mt-8">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <div className="flex items-center justify-center md:justify-start">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <span className="text-lg font-semibold">IntelliPath</span>
            </div>
            <p className="text-sm text-gray-400 mt-1 text-center md:text-left">
              Votre chemin d'apprentissage personnalisé
            </p>
          </div>
          
          <div className="text-sm text-gray-400">
            © {currentYear} IntelliPath. Tous droits réservés.
          </div>
          
          <div className="mt-4 md:mt-0">
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-white transition-colors duration-200">
                À propos
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors duration-200">
                Contact
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors duration-200">
                Aide
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;