import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState({
    id: 1,
    full_name: 'Aarav Sharma',
    email: 'wanderer@wanderwise.com',
    avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80',
    preferences: {
      preferred_styles: ['mountains', 'scenic', 'peaceful', 'coffee'],
      budget_level: 'moderate',
      travel_pace: 'balanced',
      preferred_currency: 'INR'
    }
  });
  const [token, setToken] = useState(localStorage.getItem('wanderwise_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      try {
        const profile = await api.getProfile();
        setUser(profile);
      } catch (err) {
        console.warn('Using default active traveler profile:', err);
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, [token]);

  const login = async (email, password) => {
    const data = await api.login({ email, password });
    localStorage.setItem('wanderwise_token', data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const signup = async (userData) => {
    const data = await api.signup(userData);
    localStorage.setItem('wanderwise_token', data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem('wanderwise_token');
    setToken(null);
  };

  const updatePreferences = async (newPrefs) => {
    try {
      const res = await api.updatePreferences(newPrefs);
      setUser(prev => ({ ...prev, preferences: res }));
      return res;
    } catch (err) {
      console.error('Failed to update preferences:', err);
      throw err;
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, signup, logout, updatePreferences }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

