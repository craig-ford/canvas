import { createContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { apiClient as api } from '../api/client';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'gm' | 'viewer';
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

type AuthContextType = AuthState & AuthActions;

const AuthContext = createContext<AuthContextType | undefined>(undefined);

let accessToken: string | null = null;
let isRefreshing = false;
let failedQueue: Array<{ resolve: () => void; reject: (error: any) => void }> = [];

const getAccessToken = (): string | null => accessToken;
const setAccessToken = (token: string | null): void => {
  accessToken = token;
};

export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = user !== null;

  const login = useCallback(async (email: string, password: string): Promise<void> => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, user: userData } = response.data.data;
    
    setAccessToken(access_token);
    setUser(userData);
  }, []);

  const logout = useCallback((): void => {
    setAccessToken(null);
    setUser(null);
    // Clear refresh token cookie by making request to logout endpoint
    api.post('/auth/logout').catch(() => {
      // Ignore errors on logout
    });
  }, []);

  const refreshToken = useCallback(async (): Promise<void> => {
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve: () => resolve(), reject });
      });
    }

    isRefreshing = true;
    try {
      const response = await api.post('/auth/refresh');
      const { access_token } = response.data.data;
      setAccessToken(access_token);
      
      // Process queued requests
      failedQueue.forEach(({ resolve }) => resolve());
      failedQueue = [];
    } catch (error) {
      failedQueue.forEach(({ reject }) => reject(error));
      failedQueue = [];
      throw error;
    } finally {
      isRefreshing = false;
    }
  }, []);

  // Set up axios interceptors
  useEffect(() => {
    // Request interceptor to add auth token
    const requestInterceptor = api.interceptors.request.use((config) => {
      const token = getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor to handle token refresh
    const responseInterceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401 && getAccessToken()) {
          try {
            await refreshToken();
            // Retry the original request
            const originalRequest = error.config;
            const token = getAccessToken();
            if (token) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return api.request(originalRequest);
          } catch {
            logout();
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.request.eject(requestInterceptor);
      api.interceptors.response.eject(responseInterceptor);
    };
  }, [refreshToken, logout]);

  // Attempt to restore session on mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        await refreshToken();
        // Get current user profile
        const response = await api.get('/auth/me');
        setUser(response.data.data);
      } catch {
        // No valid session
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, [refreshToken]);

  const contextValue: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export { AuthContext };