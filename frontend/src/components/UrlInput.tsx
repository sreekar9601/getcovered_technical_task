import React, { useState } from 'react';
import { Search, X, Zap } from 'lucide-react';

interface UrlInputProps {
  onSubmit: (url: string, forcePlaywright?: boolean) => void;
  isLoading: boolean;
}

export const UrlInput: React.FC<UrlInputProps> = ({ onSubmit, isLoading }) => {
  const [url, setUrl] = useState('');
  const [forcePlaywright, setForcePlaywright] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onSubmit(url.trim(), forcePlaywright);
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
      
      {/* Force Playwright Toggle */}
      <div className="mt-3 flex items-center gap-2">
        <label className="flex items-center gap-2 cursor-pointer group">
          <input
            type="checkbox"
            checked={forcePlaywright}
            onChange={(e) => setForcePlaywright(e.target.checked)}
            disabled={isLoading}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:cursor-not-allowed"
          />
          <span className="text-sm text-gray-700 group-hover:text-gray-900 flex items-center gap-1">
            <Zap size={14} className="text-orange-500" />
            <strong>Force Browser Automation</strong>
            <span className="text-gray-500">(slower, more reliable for JS-heavy sites)</span>
          </span>
        </label>
      </div>
      
      <div className="mt-6">
        <p className="text-sm text-gray-600 mb-3 font-medium">Try these popular sites:</p>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {[
            { url: 'https://github.com/login', name: 'GitHub', color: 'bg-gray-800 hover:bg-gray-900' },
            { url: 'https://stackoverflow.com/users/login', name: 'Stack Overflow', color: 'bg-orange-500 hover:bg-orange-600' },
            { url: 'https://www.linkedin.com/login', name: 'LinkedIn', color: 'bg-blue-700 hover:bg-blue-800' },
            { url: 'https://twitter.com/i/flow/login', name: 'Twitter/X', color: 'bg-black hover:bg-gray-900' },
            { url: 'https://www.reddit.com/login/', name: 'Reddit', color: 'bg-orange-600 hover:bg-orange-700' },
          ].map((example) => (
            <button
              key={example.url}
              type="button"
              onClick={() => setUrl(example.url)}
              disabled={isLoading}
              className={`${example.color} text-white px-4 py-3 rounded-lg text-sm font-medium transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-md`}
            >
              {example.name}
            </button>
          ))}
        </div>
      </div>
    </form>
  );
};

