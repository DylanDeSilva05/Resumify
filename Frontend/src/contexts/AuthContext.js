import React, { createContext, useContext, useState, useEffect } from 'react';
import apiService from '../services/apiService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = apiService.getToken();

      if (token && token !== 'demo-token') {
        // Verify token is still valid by making a test API call
        try {
          // Try to fetch actual user info to verify token
          const response = await apiService.getProfile();
          if (response) {
            setIsAuthenticated(true);
            setUser({
              token,
              user: {
                username: response.username,
                email: response.email,
                full_name: response.full_name,
                role: response.role || response.user_type  // Support both new and old field
              }
            });
          } else {
            // Token is invalid - clear it and log out
            apiService.removeToken();
            setIsAuthenticated(false);
            setUser(null);
          }
        } catch (error) {
          console.log('Token verification failed:', error);
          // Token is invalid or expired - clear it and log out
          apiService.removeToken();
          setIsAuthenticated(false);
          setUser(null);
        }
      } else {
        // No valid token - user is not authenticated
        apiService.removeToken();
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username, password, totpCode = null) => {
    try {
      const response = await apiService.login(username, password, totpCode);

      if (response.access_token) {
        apiService.setToken(response.access_token);
        setIsAuthenticated(true);
        setUser({
          token: response.access_token,
          user: response.user
        });
        // Clear settings notification dismissal on successful login
        sessionStorage.removeItem('settings_notification_dismissed');
        return { success: true };
      } else {
        return { success: false, error: 'Invalid response from server' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.message || 'Login failed',
        requiresTwoFA: error.message.includes('2FA') || error.message.includes('totp')
      };
    }
  };

  const logout = () => {
    apiService.removeToken();
    setIsAuthenticated(false);
    setUser(null);
    // Clear settings notification dismissal on logout
    sessionStorage.removeItem('settings_notification_dismissed');
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};