export interface AuthComponent {
  found: boolean;
  html_snippets: string[];
  indicators: string[];
}

export interface OAuthComponent extends AuthComponent {
  providers: string[];
}

export interface ScrapeMetadata {
  scrape_time_ms: number;
  page_title?: string;
  redirect_detected: boolean;
}

export type DetectionMethod =
  | 'static'
  | 'dynamic'
  | 'static_with_playwright_timeout'
  | 'static_after_playwright_failure';

export type ErrorType =
  | 'timeout'
  | 'bot_protection'
  | 'network_error'
  | 'ssl_error'
  | 'invalid_url'
  | 'scraping_error'
  | 'unknown';

export interface ScrapeResults {
  success: boolean;
  url: string;
  auth_found: boolean;
  scraping_method?: DetectionMethod;
  components?: {
    traditional_form: AuthComponent;
    oauth_buttons: OAuthComponent;
  };
  metadata?: ScrapeMetadata;
  error?: ErrorType;
  message?: string;
}

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';


