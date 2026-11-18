import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Sparkles, Compass, MapPin, Calendar, Users, 
  Wallet, ArrowRight, MessageSquare, CheckCircle, RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { useTrip } from '../context/TripContext';

export default function Planner() {
  const location = useLocation();
  const navigate = useNavigate();
  const { refreshTrips, openChatWithPrompt } = useTrip();

  const queryParams = new URLSearchParams(location.search);
  const initialDest = queryParams.get('destination') || 'Munnar, Kerala';
  const initialBudget = queryParams.get('budget') || '20000';
  const initialTravellers = queryParams.get('travellers') || '2';
  const initialDate = queryParams.get('date') || '2026-11-20';

  const [destination, setDestination] = useState(initialDest);
  const [startDate, setStartDate] = useState(initialDate);
  const [durationDays, setDurationDays] = useState(3);
  const [travellers, setTravellers] = useState(parseInt(initialTravellers));
  const [totalBudget, setTotalBudget] = useState(parseFloat(initialBudget));
  const [travelStyle, setTravelStyle] = useState('Scenic Exploration & Mountain Trails');
  const [mood, setMood] = useState('Peaceful & Rejuvenating');
  const [isGroup, setIsGroup] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [progressStep, setProgressStep] = useState(0);

  // Conversational prompt input
  const [promptText, setPromptText] = useState('');

  const progressMessages = [
    "Analyzing optimal routes & travel distance...",
    "Querying live Open-Meteo weather forecasts...",
    "Clustering attractions to eliminate backtracking...",
    "Balancing morning sunrise viewpoints and evening cafes...",
    "Finalizing smart budget allocations & packing checklist..."
  ];

  const handleCreateTrip = async (e) => {
    if (e) e.preventDefault();
    setGenerating(true);
    setProgressStep(0);

    const stepInterval = setInterval(() => {
      setProgressStep((prev) => (prev < progressMessages.length - 1 ? prev + 1 : prev));
    }, 700);

    try {
      // Calculate end date based on duration
      const start = new Date(startDate);
      const end = new Date(start);
      end.setDate(end.getDate() + durationDays);
      const endDateStr = end.toISOString().split('T')[0];

      const newTrip = await api.createTrip({
        title: `${destination.split(',')[0]} ${travelStyle.split('&')[0]} Expedition`,
        destination,
        country: 'India',
        start_date: startDate,
        end_date: endDateStr,
        travellers_count: travellers,
        total_budget: totalBudget,
        travel_style: travelStyle,
        mood: mood,
        is_group: isGroup
      });

      clearInterval(stepInterval);
      await refreshTrips();
      navigate(`/trips/${newTrip.id}`);
    } catch (err) {
      console.error('Trip creation error:', err);
      clearInterval(stepInterval);
      alert('Trip creation encountered an issue. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const handleNaturalLanguagePrompt = (e) => {
    e.preventDefault();
    if (!promptText.trim()) return;
    openChatWithPrompt(promptText);
    setPromptText('');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-100 text-forest-800 font-bold text-xs">
          <Sparkles className="w-3.5 h-3.5" />
          <span>AI Smart Itinerary Architect</span>
        </div>
        <h1 className="font-serif font-bold text-2xl sm:text-4xl text-slate-900">
          Plan Your Next Adventure
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 max-w-xl mx-auto">
          Describe what you want conversationally, or customize the trip parameters below to generate a day-by-day itinerary on an interactive map.
        </p>
      </div>

      {/* Natural Language Prompt Card */}
      <div className="p-6 rounded-3xl bg-forest-900 text-cream-100 shadow-soft-xl border border-forest-800 space-y-3">
        <div className="flex items-center gap-2 text-sand-300 font-semibold text-xs">
          <MessageSquare className="w-4 h-4" />
          <span>Prefer natural language? Chat directly:</span>
        </div>
        <form onSubmit={handleNaturalLanguagePrompt} className="flex gap-2">
          <input
            type="text"
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            placeholder="e.g. 'I want a 4-day peaceful trip to Munnar with coffee plantations and ₹18,000 budget for 2 friends'..."
            className="flex-1 px-4 py-3 rounded-2xl bg-forest-800/80 border border-forest-700 text-xs text-white placeholder-cream-300/50 focus:outline-none focus:ring-2 focus:ring-sand-400"
          />
          <button
            type="submit"
            className="px-5 py-3 rounded-2xl bg-sand-400 hover:bg-sand-300 text-forest-950 font-bold text-xs shrink-0 flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <Sparkles className="w-4 h-4" />
            <span className="hidden sm:inline">Ask AI</span>
          </button>
        </form>
      </div>

      {/* Structured Wizard Form */}
      <form
        onSubmit={handleCreateTrip}
        className="p-6 sm:p-8 rounded-3xl bg-white border border-sand-300 shadow-soft-md space-y-6"
      >
        <h3 className="font-serif font-bold text-lg text-slate-900 border-b border-sand-200 pb-3">
          Trip Parameters & Itinerary Configuration
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
          {/* Destination */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-700 flex items-center gap-1.5">
              <Compass className="w-4 h-4 text-forest-700" />
              <span>Destination</span>
            </label>
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              placeholder="e.g. Munnar, Kerala"
              className="w-full px-3.5 py-2.5 rounded-xl border border-sand-300 text-xs focus:ring-2 focus:ring-forest-600 font-medium"
              required
            />
          </div>

          {/* Start Date */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-700 flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-forest-700" />
              <span>Start Date</span>
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-sand-300 text-xs focus:ring-2 focus:ring-forest-600 font-medium"
              required
            />
          </div>

          {/* Duration Days */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-700 flex items-center justify-between">
              <span>Trip Duration</span>
              <span className="text-forest-700 font-bold">{durationDays} Days</span>
            </label>
            <select
              value={durationDays}
              onChange={(e) => setDurationDays(parseInt(e.target.value))}
              className="w-full px-3.5 py-2.5 rounded-xl border border-sand-300 text-xs"
            >
              <option value="2">2 Days (Weekend Getaway)</option>
              <option value="3">3 Days (Balanced Highlights)</option>
              <option value="4">4 Days (Deep Discovery)</option>
              <option value="5">5 Days (Unrushed Retreat)</option>
            </select>
          </div>

          {/* Travellers Count */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-700 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Users className="w-4 h-4 text-forest-700" />
                <span>Travellers</span>
              </span>
              <span className="text-forest-700 font-bold">{travellers} People</span>
            </label>
            <select
              value={travellers}
              onChange={(e) => setTravellers(parseInt(e.target.value))}
              className="w-full px-3.5 py-2.5 rounded-xl border border-sand-300 text-xs"
            >
              <option value="1">Solo (1 Person)</option>
              <option value="2">Couple / Duo (2 People)</option>
              <option value="3">Small Group (3 People)</option>
              <option value="4">Group (4 People)</option>
              <option value="6">Family (6 People)</option>
            </select>
          </div>

          {/* Total Budget */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-700 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Wallet className="w-4 h-4 text-forest-700" />
                <span>Total Budget (₹)</span>
              </span>
              <span className="text-forest-700 font-bold">₹{totalBudget.toLocaleString()}</span>
            </label>
            <input
              type="number"
              step="1000"
              value={totalBudget}
              onChange={(e) => setTotalBudget(parseFloat(e.target.value) || 0)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-sand-300 text-xs font-semibold text-slate-800"
              required
            />
          </div>

          {/* Travel Style */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-700">Travel Style</label>
            <select
              value={travelStyle}
              onChange={(e) => setTravelStyle(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-sand-300 text-xs"
            >
              <option value="Scenic Exploration & Mountain Trails">Scenic Exploration & Mountain Trails</option>
              <option value="Beachside Relaxation & Sunset Cafes">Beachside Relaxation & Sunset Cafes</option>
              <option value="Cultural Heritage & Heritage Haveli Stays">Cultural Heritage & Heritage Haveli Stays</option>
              <option value="High-Adrenaline Adventure & Jeep Safaris">High-Adrenaline Adventure & Jeep Safaris</option>
              <option value="Coffee Plantation Retreat & Slow Living">Coffee Plantation Retreat & Slow Living</option>
            </select>
          </div>
        </div>

        {/* Group Trip Toggle Checkbox */}
        <div className="p-4 rounded-2xl bg-cream-50 border border-sand-200 flex items-center justify-between">
          <div>
            <h4 className="font-bold text-xs text-slate-900">Enable Group Collaboration Mode</h4>
            <p className="text-[11px] text-slate-500">Generates share code for friends to vote on spots and split expenses.</p>
          </div>
          <input
            type="checkbox"
            checked={isGroup}
            onChange={(e) => setIsGroup(e.target.checked)}
            className="w-4 h-4 accent-forest-700 rounded cursor-pointer"
          />
        </div>

        {/* Loading Overlay or Submit Button */}
        {generating ? (
          <div className="p-6 rounded-2xl bg-forest-900 text-cream-100 text-center space-y-3">
            <RefreshCw className="w-8 h-8 text-sand-300 animate-spin mx-auto" />
            <h4 className="font-serif font-bold text-base text-white">Synthesizing Your Smart Itinerary</h4>
            <p className="text-xs text-sand-300 font-mono">{progressMessages[progressStep]}</p>
          </div>
        ) : (
          <button
            type="submit"
            className="w-full py-4 rounded-2xl bg-forest-800 hover:bg-forest-700 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-soft-md transition-all hover:scale-[1.01] active:scale-[0.99]"
          >
            <Sparkles className="w-4 h-4 text-sand-300" />
            <span>Generate Smart Itinerary & Interactive Map</span>
          </button>
        )}
      </form>
    </div>
  );
}
