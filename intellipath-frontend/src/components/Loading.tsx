interface LoadingProps {
  message?: string;
}

const Loading: React.FC<LoadingProps> = ({ message = 'Chargement en cours...' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="relative">
        <div className="h-16 w-16 rounded-full border-t-4 border-b-4 border-primary animate-spin"></div>
        <div className="absolute top-0 left-0 h-16 w-16 rounded-full border-t-4 border-b-4 border-secondary animate-spin" style={{ animationDirection: 'reverse', opacity: 0.7 }}></div>
      </div>
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
};

export default Loading;