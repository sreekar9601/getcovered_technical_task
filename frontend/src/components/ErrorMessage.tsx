import React from 'react';
import { AlertCircle, RefreshCw, Clock, Shield, Wifi, Lock, Link } from 'lucide-react';
import { ErrorType } from '../types';

interface ErrorMessageProps {
  error: ErrorType;
  message?: string;
  onRetry: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ error, message, onRetry }) => {
  const getErrorDetails = () => {
    switch (error) {
      case 'timeout':
        return {
          icon: Clock,
          title: 'Request Timed Out',
          color: 'yellow',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          textColor: 'text-yellow-900',
          iconColor: 'text-yellow-600',
          badgeColor: 'bg-yellow-100 text-yellow-800',
          suggestion: 'The website took too long to respond. Try again or check if the site is accessible.'
        };
      case 'bot_protection':
        return {
          icon: Shield,
          title: 'Bot Protection Detected',
          color: 'red',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-900',
          iconColor: 'text-red-600',
          badgeColor: 'bg-red-100 text-red-800',
          suggestion: 'This site uses Cloudflare or similar bot protection. Try accessing the site directly in your browser.'
        };
      case 'network_error':
        return {
          icon: Wifi,
          title: 'Network Error',
          color: 'orange',
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-200',
          textColor: 'text-orange-900',
          iconColor: 'text-orange-600',
          badgeColor: 'bg-orange-100 text-orange-800',
          suggestion: 'Could not connect to the website. Check your internet connection or verify the URL.'
        };
      case 'ssl_error':
        return {
          icon: Lock,
          title: 'SSL Certificate Error',
          color: 'purple',
          bgColor: 'bg-purple-50',
          borderColor: 'border-purple-200',
          textColor: 'text-purple-900',
          iconColor: 'text-purple-600',
          badgeColor: 'bg-purple-100 text-purple-800',
          suggestion: 'The website has an invalid or expired SSL certificate.'
        };
      case 'invalid_url':
        return {
          icon: Link,
          title: 'Invalid URL',
          color: 'gray',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          textColor: 'text-gray-900',
          iconColor: 'text-gray-600',
          badgeColor: 'bg-gray-100 text-gray-800',
          suggestion: 'Please provide a valid URL (e.g., https://example.com)'
        };
      case 'scraping_error':
        return {
          icon: AlertCircle,
          title: 'Scraping Error',
          color: 'red',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-900',
          iconColor: 'text-red-600',
          badgeColor: 'bg-red-100 text-red-800',
          suggestion: 'Failed to scrape the website. The site may be blocking automated access.'
        };
      default:
        return {
          icon: AlertCircle,
          title: 'Unknown Error',
          color: 'red',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-900',
          iconColor: 'text-red-600',
          badgeColor: 'bg-red-100 text-red-800',
          suggestion: 'An unexpected error occurred. Please try again.'
        };
    }
  };

  const details = getErrorDetails();
  const Icon = details.icon;

  return (
    <div className={`w-full max-w-3xl mx-auto mt-8 p-6 ${details.bgColor} border-2 ${details.borderColor} rounded-lg animate-fade-in`}>
      <div className="flex items-start gap-3">
        <Icon className={`w-6 h-6 ${details.iconColor} flex-shrink-0 mt-0.5`} />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className={`text-lg font-semibold ${details.textColor}`}>{details.title}</h3>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${details.badgeColor}`}>
              {error}
            </span>
          </div>

          {message && <p className={`mt-2 ${details.textColor} opacity-90`}>{message}</p>}

          <p className={`mt-3 text-sm ${details.textColor} opacity-75`}>
            💡 {details.suggestion}
          </p>
        </div>
      </div>

      <button
        onClick={onRetry}
        className={`mt-4 px-4 py-2 bg-${details.color}-600 text-white rounded-md hover:bg-${details.color}-700 flex items-center gap-2 transition-colors`}
      >
        <RefreshCw size={18} />
        Try Again
      </button>
    </div>
  );
};

