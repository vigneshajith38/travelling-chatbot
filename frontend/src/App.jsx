import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { TripProvider } from './context/TripContext';

// Core AI Travel Chatbot - WanderWise
import ChatbotView from './pages/ChatbotView';

export default function App() {
  return (
    <AuthProvider>
      <TripProvider>
        <Router>
          <div className="h-screen w-screen overflow-hidden bg-cream-100 font-sans text-slate-900 select-none">
            <Routes>
              {/* Pure Chatbot Architecture: every route directly lands into the WanderWise AI Copilot */}
              <Route path="/" element={<ChatbotView />} />
              <Route path="/chat" element={<ChatbotView />} />
              <Route path="/chat/:sessionId" element={<ChatbotView />} />
              <Route path="*" element={<ChatbotView />} />
            </Routes>
          </div>
        </Router>
      </TripProvider>
    </AuthProvider>
  );
}
