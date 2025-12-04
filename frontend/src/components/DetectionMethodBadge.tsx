import React from 'react';
import { Zap, Drama, Bot, AlertCircle } from 'lucide-react';

interface DetectionMethodBadgeProps {
    method: string;
}

export const DetectionMethodBadge: React.FC<DetectionMethodBadgeProps> = ({ method }) => {
    const getMethodDetails = () => {
        if (method === 'static') {
            return {
                icon: Zap,
                label: 'Static HTML',
                color: 'bg-green-100 text-green-800 border-green-200',
                tooltip: 'Fast HTTP scraping - no JavaScript execution'
            };
        } else if (method === 'dynamic') {
            return {
                icon: Drama,
                label: 'Playwright',
                color: 'bg-blue-100 text-blue-800 border-blue-200',
                tooltip: 'Browser automation - JavaScript rendered content'
            };
        } else if (method.includes('playwright_timeout')) {
            return {
                icon: AlertCircle,
                label: 'Static (Playwright Timeout)',
                color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
                tooltip: 'Playwright timed out, using static HTML as fallback'
            };
        } else if (method.includes('playwright_failure')) {
            return {
                icon: Bot,
                label: 'Static (LLM Fallback)',
                color: 'bg-purple-100 text-purple-800 border-purple-200',
                tooltip: 'Playwright failed, using static HTML with LLM detection'
            };
        }

        return {
            icon: AlertCircle,
            label: method,
            color: 'bg-gray-100 text-gray-800 border-gray-200',
            tooltip: 'Unknown detection method'
        };
    };

    const { icon: Icon, label, color, tooltip } = getMethodDetails();

    return (
        <div className="group relative inline-flex">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${color} text-sm font-medium`}>
                <Icon size={16} />
                <span>{label}</span>
            </div>

            {/* Tooltip */}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                {tooltip}
                <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900"></div>
            </div>
        </div>
    );
};
