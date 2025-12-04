import { useState } from 'react';
import { Lock } from 'lucide-react';
import { UrlInput } from './components/UrlInput';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorMessage } from './components/ErrorMessage';
import { ResultsDisplay } from './components/ResultsDisplay';
import { scrapeWebsite } from './services/api';
import { ScrapeResults, LoadingState } from './types';

function App() {
  const [loadingState, setLoadingState] = useState<LoadingState>('idle');
  const [results, setResults] = useState<ScrapeResults | null>(null);
  const [lastUrl, setLastUrl] = useState<string>('');

  const handleSubmit = async (url: string, forcePlaywright: boolean = false) => {
    setLastUrl(url);
    setLoadingState('loading');
    setResults(null);

    try {
      const data = await scrapeWebsite(url, forcePlaywright);
      setResults(data);
      setLoadingState('success');
    } catch (error) {
      setResults({
        success: false,
        url,
        auth_found: false,
        error: 'network_error',
        message: error instanceof Error ? error.message : 'An unexpected error occurred',
      });
      setLoadingState('error');
    }
  };

  const handleRetry = () => {
    if (lastUrl) {
      handleSubmit(lastUrl);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Lock className="w-12 h-12 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Login Form Detector</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Detect authentication components on any website. Identifies traditional login forms and OAuth/SSO buttons.
          </p>
        </div>

        {/* URL Input */}
        <UrlInput 
          onSubmit={handleSubmit} 
          isLoading={loadingState === 'loading'} 
        />

        {/* Loading State */}
        {loadingState === 'loading' && <LoadingSpinner />}

        {/* Error State */}
        {loadingState === 'error' && results && !results.success && (
          <ErrorMessage 
            error={results.error || 'unknown'}
            message={results.message}
            onRetry={handleRetry}
          />
        )}

        {/* Results */}
        {loadingState === 'success' && results && <ResultsDisplay results={results} />}

        {/* Footer */}
        <div className="mt-16 text-center text-sm text-gray-500">
          <p>Built with React + FastAPI + requests/BeautifulSoup + Playwright</p>
          <p className="mt-2">Supports both static HTML and JavaScript-rendered sites</p>
        </div>
      </div>
    </div>
  );
}

export default App;
