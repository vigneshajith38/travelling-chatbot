import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const TripContext = createContext(null);

export function TripProvider({ children }) {
  const [trips, setTrips] = useState([]);
  const [activeTrip, setActiveTrip] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [prefilledPrompt, setPrefilledPrompt] = useState('');

  const fetchTrips = async () => {
    setLoading(true);
    try {
      const data = await api.getTrips();
      setTrips(data);
      if (data.length > 0 && !activeTrip) {
        setActiveTrip(data[0]);
      }
    } catch (err) {
      console.error('Failed to load trips:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrips();
  }, []);

  const openChatWithPrompt = (promptText = '') => {
    setPrefilledPrompt(promptText);
    setIsChatOpen(true);
  };

  return (
    <TripContext.Provider value={{
      trips,
      activeTrip,
      setActiveTrip,
      loading,
      refreshTrips: fetchTrips,
      isChatOpen,
      setIsChatOpen,
      prefilledPrompt,
      setPrefilledPrompt,
      openChatWithPrompt
    }}>
      {children}
    </TripContext.Provider>
  );
}

export function useTrip() {
  const context = useContext(TripContext);
  if (!context) {
    throw new Error('useTrip must be used within a TripProvider');
  }
  return context;
}

