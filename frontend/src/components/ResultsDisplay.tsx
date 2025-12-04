import React, { useState } from 'react';
import { ScrapeResults } from '../types';
import { CheckCircle, XCircle, Code, Copy, Check, Clock, FileText } from 'lucide-react';
import { DetectionMethodBadge } from './DetectionMethodBadge';

interface ResultsDisplayProps {
  results: ScrapeResults;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  const [activeTab, setActiveTab] = useState<'traditional' | 'oauth' | 'json'>('traditional');
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  if (!results.success || !results.auth_found) {
    return (
      <div className="w-full max-w-4xl mx-auto mt-8 p-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg">
        <div className="flex items-center gap-3">
          <XCircle className="w-6 h-6 text-yellow-600" />
          <div>
            <h3 className="text-lg font-semibold text-yellow-900">No Authentication Found</h3>
            <p className="mt-1 text-yellow-700">
              {results.message || 'No login forms or authentication components were detected on this page.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const { components, metadata } = results;
  const traditional = components?.traditional_form;
  const oauth = components?.oauth_buttons;

  return (
    <div className="w-full max-w-4xl mx-auto mt-8 animate-fade-in">
      {/* Success Banner */}
      <div className="p-6 bg-green-50 border-2 border-green-200 rounded-lg mb-6">
        <div className="flex items-center gap-3">
          <CheckCircle className="w-6 h-6 text-green-600" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-green-900">Authentication Components Found!</h3>
            <div className="mt-3 flex flex-wrap gap-3 items-center">
              <DetectionMethodBadge method={results.scraping_method || 'unknown'} />
              <div className="flex items-center gap-2 text-sm text-green-700">
                <Clock size={14} />
                <span><strong>{metadata?.scrape_time_ms}ms</strong></span>
              </div>
              {metadata?.page_title && (
                <span className="text-sm text-green-700">
                  Page: <strong>{metadata.page_title}</strong>
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b-2 border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('traditional')}
          className={`px-6 py-3 font-medium transition-colors ${activeTab === 'traditional'
              ? 'text-blue-600 border-b-2 border-blue-600 -mb-0.5'
              : 'text-gray-600 hover:text-gray-900'
            }`}
        >
          <div className="flex items-center gap-2">
            <FileText size={18} />
            Traditional Forms
            {traditional?.found && <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">{traditional.html_snippets.length}</span>}
          </div>
        </button>

        <button
          onClick={() => setActiveTab('oauth')}
          className={`px-6 py-3 font-medium transition-colors ${activeTab === 'oauth'
              ? 'text-blue-600 border-b-2 border-blue-600 -mb-0.5'
              : 'text-gray-600 hover:text-gray-900'
            }`}
        >
          <div className="flex items-center gap-2">
            <Code size={18} />
            OAuth/SSO
            {oauth?.found && <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">{oauth.providers.length}</span>}
          </div>
        </button>

        <button
          onClick={() => setActiveTab('json')}
          className={`px-6 py-3 font-medium transition-colors ${activeTab === 'json'
              ? 'text-blue-600 border-b-2 border-blue-600 -mb-0.5'
              : 'text-gray-600 hover:text-gray-900'
            }`}
        >
          <div className="flex items-center gap-2">
            <Code size={18} />
            Raw JSON
          </div>
        </button>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'traditional' && traditional && (
          <div>
            {traditional.found ? (
              <>
                <div className="mb-4 flex gap-2 flex-wrap">
                  <span className="text-sm text-gray-600">Indicators:</span>
                  {traditional.indicators.map((indicator) => (
                    <span key={indicator} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                      {indicator}
                    </span>
                  ))}
                </div>

                {traditional.html_snippets.map((snippet, index) => (
                  <div key={index} className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="text-sm font-medium text-gray-700">Form #{index + 1}</h4>
                      <button
                        onClick={() => copyToClipboard(snippet, index)}
                        className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded flex items-center gap-2"
                      >
                        {copiedIndex === index ? <Check size={14} /> : <Copy size={14} />}
                        {copiedIndex === index ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <pre className="p-4 bg-gray-900 text-green-400 text-sm rounded-lg overflow-x-auto">
                      <code>{snippet}</code>
                    </pre>
                  </div>
                ))}
              </>
            ) : (
              <p className="text-gray-500">No traditional login forms detected.</p>
            )}
          </div>
        )}

        {activeTab === 'oauth' && oauth && (
          <div>
            {oauth.found ? (
              <>
                <div className="mb-4 flex gap-2 flex-wrap">
                  <span className="text-sm text-gray-600">Providers:</span>
                  {oauth.providers.map((provider) => (
                    <span key={provider} className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full capitalize">
                      {provider}
                    </span>
                  ))}
                </div>

                {oauth.html_snippets.map((snippet, index) => (
                  <div key={index} className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="text-sm font-medium text-gray-700">OAuth Button #{index + 1}</h4>
                      <button
                        onClick={() => copyToClipboard(snippet, 100 + index)}
                        className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded flex items-center gap-2"
                      >
                        {copiedIndex === 100 + index ? <Check size={14} /> : <Copy size={14} />}
                        {copiedIndex === 100 + index ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <pre className="p-4 bg-gray-900 text-green-400 text-sm rounded-lg overflow-x-auto">
                      <code>{snippet}</code>
                    </pre>
                  </div>
                ))}
              </>
            ) : (
              <p className="text-gray-500">No OAuth/SSO buttons detected.</p>
            )}
          </div>
        )}

        {activeTab === 'json' && (
          <div>
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium text-gray-700">Full API Response</h4>
              <button
                onClick={() => copyToClipboard(JSON.stringify(results, null, 2), 999)}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded flex items-center gap-2"
              >
                {copiedIndex === 999 ? <Check size={14} /> : <Copy size={14} />}
                {copiedIndex === 999 ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <pre className="p-4 bg-gray-900 text-green-400 text-sm rounded-lg overflow-x-auto">
              <code>{JSON.stringify(results, null, 2)}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

