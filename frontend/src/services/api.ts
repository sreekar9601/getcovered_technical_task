import axios from 'axios';
import { ScrapeResults } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ScrapeRequest {
  url: string;
}

export const scrapeWebsite = async (url: string): Promise<ScrapeResults> => {
  try {
    const response = await axios.post<ScrapeResults>(
      `${API_BASE_URL}/api/scrape`,
      { url },
      {
        timeout: 60000, // 60 second timeout
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // Server responded with error
        return error.response.data;
      } else if (error.request) {
        // Request made but no response
        throw new Error('No response from server. Please check your connection.');
      }
    }
    throw new Error('An unexpected error occurred.');
  }
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/health`, {
      timeout: 5000,
    });
    return response.data.status === 'healthy';
  } catch {
    return false;
  }
};

