import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

console.error('[INFO] api.js loaded! Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor - ALWAYS attach token if available
api.interceptors.request.use(
  (config) => {
    // Debug logging - using error to ensure visibility
    console.error(`[API] API Request: ${config.method?.toUpperCase()} ${config.url}`);

    // Skip auth for login/register
    if (config.url?.includes('/auth/login') || config.url?.includes('/auth/register')) {
      console.error('[SKIP] Skipping auth for login/register');
      return config;
    }

    // Get token from localStorage
    let token = localStorage.getItem('serenity_token');
    
    // Validate token format (JWT tokens start with 'eyJ')
    if (token) {
      token = token.trim();
      if (!token.startsWith('eyJ')) {
        console.error('[WARN] Invalid token format (should start with eyJ):', token.substring(0, 20));
        token = null; // Treat as invalid
      }
    }
    
    console.error('[TOKEN] Token in localStorage:', token ? `${token.substring(0, 10)}...` : 'MISSING');

    // Ensure headers object exists
    if (!config.headers) {
      config.headers = {};
    }

    if (token && token.trim()) {
      // Token is valid - attach it
      const bearerToken = `Bearer ${token.trim()}`;
      
      // Set Authorization header explicitly - use both bracket and dot notation
      config.headers['Authorization'] = bearerToken;
      config.headers.Authorization = bearerToken; // Also set as property for compatibility
      
      // Also set on common headers as fallback
      api.defaults.headers.common['Authorization'] = bearerToken;
      api.defaults.headers.common.Authorization = bearerToken;

      console.error('[OK] Attached Authorization header:', bearerToken.substring(0, 20) + '...');
    } else {
      console.error('[WARN] No valid token found for request to:', config.url);
      // Remove any existing Authorization header if no token
      delete config.headers['Authorization'];
      delete config.headers.Authorization;
      delete api.defaults.headers.common['Authorization'];
      delete api.defaults.headers.common.Authorization;
    }

    // Log final headers for debugging
    const headersToLog = {};
    Object.keys(config.headers).forEach(key => {
      if (key.toLowerCase() === 'authorization') {
        headersToLog[key] = config.headers[key] ? config.headers[key].substring(0, 20) + '...' : 'NOT SET';
      } else {
        headersToLog[key] = config.headers[key];
      }
    });
    console.error('[HEADERS] Final Headers:', headersToLog);

    return config;
  },
  (error) => {
    console.error('[ERROR] Interceptor Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('[ERROR] 401 Unauthorized received in interceptor');
      // DEBUG: Commented out clearing to investigate persistence
      // localStorage.removeItem('serenity_token');
      // localStorage.removeItem('serenity_user');
      // Redirect to login
      /*
      if (!window.location.pathname.includes('login')) {
        window.location.href = '/';
      }
      */
    }
    return Promise.reject(error);
  }
);

export default api;
