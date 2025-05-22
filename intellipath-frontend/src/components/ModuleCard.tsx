import { useState } from 'react';
import { Module } from '../types';
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/24/outline';

interface ModuleCardProps {
  module: Module;
  index: number;
  onQuizClick: (index: number) => void;
}

const ModuleCard: React.FC<ModuleCardProps> = ({ module, index, onQuizClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="card mb-4 border-l-4 border-primary transition-all hover:shadow-lg">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-xl font-bold text-primary-dark">
            Module {index + 1}: {module.title}
          </h3>
          <p className="text-sm text-gray-500 mt-1">{module.duration}</p>
        </div>
        <button
          onClick={toggleExpand}
          className="p-1 rounded-full hover:bg-gray-100"
          aria-expanded={isExpanded}
          aria-label={isExpanded ? "Réduire" : "Développer"}
        >
          {isExpanded ? (
            <ChevronUpIcon className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronDownIcon className="h-5 w-5 text-gray-500" />
          )}
        </button>
      </div>

      <div className="mt-2">
        <p className="text-gray-700">{module.description}</p>
      </div>

      {isExpanded && (
        <div className="mt-4 space-y-4">
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Sujets abordés :</h4>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              {module.topics.map((topic, i) => (
                <li key={i} className="ml-2">{topic}</li>
              ))}
            </ul>
          </div>

          {module.resources && module.resources.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Ressources :</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {module.resources.map((resource, i) => (
                  <li key={i} className="ml-2">{resource}</li>
                ))}
              </ul>
            </div>
          )}

          {module.projects && module.projects.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Projets :</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {module.projects.map((project, i) => (
                  <li key={i} className="ml-2">{project}</li>
                ))}
              </ul>
            </div>
          )}

          {module.assessments && module.assessments.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Évaluations :</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {module.assessments.map((assessment, i) => (
                  <li key={i} className="ml-2">{assessment}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-4 flex justify-end">
            <button
              onClick={() => onQuizClick(index)}
              className="btn-secondary flex items-center space-x-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
              </svg>
              <span>Quiz sur ce module</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModuleCard;