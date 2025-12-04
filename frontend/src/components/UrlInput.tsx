import React, { useState } from 'react';
import { Search, X } from 'lucide-react';

interface UrlInputProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
}

export const UrlInput: React.FC<UrlInputProps> = ({ onSubmit, isLoading }) => {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onSubmit(url.trim());
    }
  };

  const handleClear = () => {
    setUrl('');
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      <div className="relative flex items-center">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter website URL (e.g., https://github.com/login)"
          className="w-full px-4 py-3 pr-24 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          disabled={isLoading}
        />
        
        {url && !isLoading && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-20 p-1 text-gray-400 hover:text-gray-600"
          >
            <X size={20} />
          </button>
        )}
        
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="absolute right-2 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Search size={18} />
          Analyze
        </button>
      </div>
      
      <div className="mt-3 flex gap-2 flex-wrap">
        <span className="text-sm text-gray-500">Try:</span>
        {['https://github.com/login', 'https://stackoverflow.com/users/login', 'https://www.linkedin.com/login'].map((exampleUrl) => (
          <button
            key={exampleUrl}
            type="button"
            onClick={() => setUrl(exampleUrl)}
            disabled={isLoading}
            className="text-sm text-blue-600 hover:text-blue-800 hover:underline disabled:text-gray-400"
          >
            {exampleUrl.split('//')[1].split('/')[0]}
          </button>
        ))}
      </div>
    </form>
  );
};

