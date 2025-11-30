import { reactive } from 'vue';
import api from '../services/api';

// Helper to safely parse JSON from localStorage
const getStoredUser = () => {
  try {
    const token = localStorage.getItem('serenity_token');
    // Only return user if we also have a valid token that looks like a JWT
    if (!token || !token.trim() || !token.startsWith('eyJ')) {
      return null;
    }

    const userStr = localStorage.getItem('serenity_user');
    if (!userStr || userStr === 'null') return null;
    return JSON.parse(userStr);
  } catch (e) {
    console.error('Error parsing stored user:', e);
    return null;
  }
};

const state = reactive({
  user: getStoredUser(),
  token: (() => {
    const token = localStorage.getItem('serenity_token');
    // Only return token if it's a valid JWT format
    if (token && token.trim() && token.startsWith('eyJ')) {
      return token;
    }
    return '';
  })(),
  loading: false,
  error: ''
});

export function useAuthStore() {
  const setSession = (user, token) => {
    if (!token) {
      console.error('Attempted to set session with empty token!');
      return;
    }

    // Store in localStorage FIRST, before updating reactive state
    // This prevents race conditions where components mount before token is available
    try {
      // Clear any existing data first
      localStorage.removeItem('serenity_token');
      localStorage.removeItem('serenity_user');

      // Store new data
      localStorage.setItem('serenity_token', token);
      localStorage.setItem('serenity_user', JSON.stringify(user));

      // Immediately verify it was stored
      const verifyToken = localStorage.getItem('serenity_token');
      const verifyUser = localStorage.getItem('serenity_user');

      if (verifyToken !== token) {
        console.error('Token storage verification failed');
        return;
      }

      if (!verifyUser) {
        console.error('User data storage verification failed');
        return;
      }

      // Update reactive state
      state.user = user;
      state.token = token;

    } catch (error) {
      console.error('Error storing session in localStorage:', error);
      throw error; // Re-throw so caller knows it failed
    }
  };

  const clearSession = () => {
    state.user = null;
    state.token = '';
    localStorage.removeItem('serenity_user');
    localStorage.removeItem('serenity_token');
  };

  const login = async (credentials) => {
    state.loading = true;
    state.error = '';
    try {
      const { data } = await api.post('/auth/login', credentials);

      if (!data.access_token) {
        console.error('No access token received from server');
        throw new Error('No access token received from server');
      }

      setSession(data.user, data.access_token);

      // Verify token was stored
      await new Promise(resolve => setTimeout(resolve, 10));
      const storedToken = localStorage.getItem('serenity_token');
      if (!storedToken) {
        // Fallback: store directly if setSession didn't work
        localStorage.setItem('serenity_token', data.access_token);
        localStorage.setItem('serenity_user', JSON.stringify(data.user));
        state.user = data.user;
        state.token = data.access_token;
      }

      return data;
    } catch (error) {
      state.error = error.response?.data?.error || 'Login failed';
      throw error;
    } finally {
      state.loading = false;
    }
  };

  const register = async (userData) => {
    state.loading = true;
    state.error = '';
    try {
      const { data } = await api.post('/auth/register', userData);
      setSession(data.user, data.access_token);
      return data;
    } catch (error) {
      state.error = error.response?.data?.error || 'Registration failed';
      throw error;
    } finally {
      state.loading = false;
    }
  };

  return {
    state,
    setSession,
    clearSession,
    login,
    register
  };
}

