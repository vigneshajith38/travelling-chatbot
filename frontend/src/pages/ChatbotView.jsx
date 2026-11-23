import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send, Sparkles, Compass, MapPin, Calendar,
  Users, Wallet, Sliders, ShieldCheck, Luggage,
  CloudRain, Plus, Trash2, ArrowRight, CheckCircle2,
  MessageSquare, Zap, RefreshCw, ChevronDown, ChevronUp, Star,
  PanelLeftClose, PanelLeftOpen, Search, X, Check, Eye, HelpCircle, Layers
} from 'lucide-react';
import { api } from '../services/api';
import InteractiveMap from '../components/maps/InteractiveMap';
import WhatIfSimulatorModal from '../components/simulator/WhatIfSimulatorModal';

const PRESET_STARTER_CARDS = [
  {
    icon: "🌴",
    title: "Discover Bali & Hidden Beaches",
    subtitle: "Culture, volcanic hikes & coastal vibe",
    prompt: "Tell me about Bali. What are the best areas to stay, cultural highlights, and secret beaches away from crowds?"
  },
  {
    icon: "🇮🇳",
    title: "5 Days Golden Triangle & India",
    subtitle: "Delhi, Agra Taj Mahal & Jaipur forts",
    prompt: "Plan a 5-day trip to India covering historic Delhi, sunrise at the Taj Mahal in Agra, and royal Jaipur palaces under ₹30,000 for 2."
  },
  {
    icon: "🏖️",
    title: "4 Days in Goa",
    subtitle: "Heritage quarters & beach sunsets",
    prompt: "Plan a 4-day coastal trip to Goa with Portuguese Fontainhas walks, Dudhsagar falls, and sunset cafes under ₹20,000 for 2."
  },
  {
    icon: "⚡",
    title: "DeepSearch Hidden Gems",
    subtitle: "Offbeat trails, terrain & golden hours",
    prompt: "Run DeepSearch on Manali: uncover secret cedar trails, golden-hour photo spots, and authentic Himachali food secrets.",
    isDeepSearch: true
  },
  {
    icon: "🗼",
    title: "Paris Highlights",
    subtitle: "Art, architecture & Seine cruises",
    prompt: "Plan a 5-day trip to Paris with iconic monuments, Latin Quarter bistros, and an evening Seine cruise."
  }
];

const QUICK_MOOD_PROMPTS = [
  "🇮🇳 5 Days in India",
  "🏖️ 4 Days in Goa",
  "🏔️ 5 Days in Manali",
  "🌴 6 Days in Kerala",
  "🏨 Hotels in Delhi & Goa",
  "✈️ Trains & Flights Mumbai to Goa",
  "💰 Budget trip under ₹20k"
];

export default function ChatbotView() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [deepSearchEnabled, setDeepSearchEnabled] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTabByMsgId, setActiveTabByMsgId] = useState({});
  const [showMemoryModal, setShowMemoryModal] = useState(false);

  // Bot persistent memory state
  const [memoryState, setMemoryState] = useState({
    destination: null,
    days: 3,
    budget: 20000.0,
    travellers: 2,
    interests: []
  });

  // Modal states
  const [simulatorTrip, setSimulatorTrip] = useState(null);
  const [showSimulator, setShowSimulator] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadSessions = async () => {
    try {
      const data = await api.getChatSessions();
      setSessions(data);
    } catch (err) {
      console.warn('Sessions load warning:', err);
    }
  };

  const handleSendMessage = async (textToSend = null, forceDeepSearch = null) => {
    const text = textToSend || inputMessage.trim();
    if (!text || loading) return;

    const useDeepSearch = forceDeepSearch !== null ? forceDeepSearch : deepSearchEnabled;

    // Reset DeepSearch toggle after firing so next regular messages aren't trapped in deepsearch
    if (deepSearchEnabled) {
      setDeepSearchEnabled(false);
    }

    const userMsg = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: text,
      is_deep_search: useDeepSearch
    };
    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await api.sendChatMessage({
        message: text,
        session_id: sessionId,
        deep_search: useDeepSearch
      });

      if (response.session_id) {
        setSessionId(response.session_id);
      }

      if (response.memory) {
        setMemoryState(response.memory);
      }

      const newMsgId = response.message.id || `asst_${Date.now()}`;
      setMessages(prev => [...prev, {
        id: newMsgId,
        role: 'assistant',
        content: response.message.content,
        structured_type: response.message.structured_type,
        structured_data: response.message.structured_data,
        suggested_actions: response.suggested_actions
      }]);

      // Default active tab for itinerary to 'schedule'
      if (response.message.structured_type === 'itinerary_preview') {
        setActiveTabByMsgId(prev => ({ ...prev, [newMsgId]: 'schedule' }));
      }

      await loadSessions();
    } catch (err) {
      console.error('Chat error:', err);
      const destName = memoryState.destination || 'your destination';
      const errorReplies = [
        `I hit a brief connection delay reaching the live intelligence servers. I still have your context saved (${destName}). Please verify the backend is running and ask again!`,
        `Network hiccup on my end while fetching the latest travel data for **${destName}**. Please try asking your question again in a moment.`
      ];
      const reply = errorReplies[Math.floor(Math.random() * errorReplies.length)];
      setMessages(prev => [...prev, {
        id: `asst_err_${Date.now()}`,
        role: 'assistant',
        content: reply,
        structured_type: null
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleStartNewChat = () => {
    setSessionId(null);
    setMemoryState({
      destination: null,
      days: 3,
      budget: 20000.0,
      travellers: 2,
      interests: []
    });
    setMessages([]);
  };

  const handleSelectSession = async (sId) => {
    if (sId === sessionId) return;
    setLoading(true);
    try {
      const sessionData = await api.getChatSessionDetail(sId);
      setSessionId(sId);
      if (sessionData.context_state) {
        setMemoryState(sessionData.context_state);
      }
      if (sessionData.messages && sessionData.messages.length > 0) {
        setMessages(sessionData.messages);
      } else {
        setMessages([]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (e, sId) => {
    e.stopPropagation();
    try {
      await api.deleteChatSession(sId);
      if (sessionId === sId) {
        handleStartNewChat();
      }
      await loadSessions();
    } catch (err) {
      console.error('Delete chat error:', err);
    }
  };

  const handleAction = async (actionItem) => {
    if (actionItem.action === 'open_link' && actionItem.url) {
      window.open(actionItem.url, '_blank', 'noopener,noreferrer');
      return;
    } else if (actionItem.action === 'prompt') {
      handleSendMessage(actionItem.text);
    } else if (actionItem.action === 'deep_search') {
      setDeepSearchEnabled(true);
      handleSendMessage(`DeepSearch ${actionItem.destination}: find offbeat spots, terrain advisories, and local culinary trails.`, true);
    } else if (actionItem.action === 'generate_itinerary') {
      handleSendMessage(`Create a full ${memoryState.days || 3}-day itinerary for ${actionItem.destination}`);
    } else if (actionItem.action === 'open_simulator') {
      setSimulatorTrip({
        id: 1,
        destination: memoryState.destination || 'Paris, France',
        total_budget: memoryState.budget || 20000.0,
        travellers_count: memoryState.travellers || 2
      });
      setShowSimulator(true);
    } else if (actionItem.action === 'check_weather') {
      handleSendMessage(`Check live weather for ${memoryState.destination || 'Paris, France'} and suggest outdoor vs indoor timing.`);
    } else {
      handleSendMessage(actionItem.label);
    }
  };

  const filteredSessions = sessions.filter(s =>
    !searchQuery || (s.title && s.title.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="flex h-screen w-screen bg-[#fcfaf7] font-sans text-slate-800 overflow-hidden">
      {/* ======================================================== */}
      {/* 1. COLLAPSIBLE CHATBOT SIDEBAR (ChatGPT / Claude Style)   */}
      {/* ======================================================== */}
      <aside
        className={`${sidebarOpen ? 'w-80' : 'w-0 -translate-x-full'
          } transition-all duration-300 ease-in-out bg-[#0f241d] text-cream-100 flex flex-col border-r border-forest-900/60 shrink-0 z-30 overflow-hidden relative shadow-soft-lg`}
      >
        {/* Brand & New Chat */}
        <div className="p-4 border-b border-forest-800/60 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-500 to-skycoast-400 flex items-center justify-center shadow-md">
                <Compass className="w-5 h-5 text-forest-950 animate-spin" style={{ animationDuration: '24s' }} />
              </div>
              <div>
                <span className="font-serif text-base font-bold text-white tracking-tight block leading-tight">
                  WanderWise
                </span>
                <span className="text-[10px] uppercase font-bold tracking-widest text-emerald-400">
                  AI Travel Copilot
                </span>
              </div>
            </div>

            <button
              onClick={() => setSidebarOpen(false)}
              className="p-1.5 rounded-lg text-cream-300/70 hover:text-white hover:bg-forest-800/80 transition-colors"
              title="Close sidebar"
            >
              <PanelLeftClose className="w-4 h-4" />
            </button>
          </div>

          {/* New Chat Button */}
          <button
            onClick={handleStartNewChat}
            className="w-full py-2 px-3 rounded-xl bg-forest-800/90 hover:bg-forest-700/90 text-white font-semibold text-xs flex items-center justify-center gap-2 border border-emerald-500/30 transition-all shadow-sm group"
          >
            <Plus className="w-4 h-4 text-emerald-400 group-hover:rotate-90 transition-transform" />
            <span>New Travel Conversation</span>
          </button>
        </div>

        {/* DeepSearch Mode Pill in Sidebar */}
        <div className="px-3 pt-3">
          <div
            onClick={() => setDeepSearchEnabled(!deepSearchEnabled)}
            className={`p-2.5 rounded-xl cursor-pointer border transition-all flex items-center justify-between ${deepSearchEnabled
              ? 'bg-emerald-950/80 border-emerald-500/70 text-white shadow-soft-sm'
              : 'bg-forest-900/50 border-forest-800/60 text-cream-300/80 hover:bg-forest-800/60'
              }`}
          >
            <div className="flex items-center gap-2">
              <div className={`p-1.5 rounded-lg ${deepSearchEnabled ? 'bg-emerald-500 text-forest-950' : 'bg-forest-800 text-emerald-400'}`}>
                <Zap className="w-3.5 h-3.5" />
              </div>
              <div>
                <span className="font-bold text-xs block text-cream-100">DeepSearch ⚡ Mode</span>
                <span className="text-[10px] text-cream-400/80 block">Offbeat trails & terrain intel</span>
              </div>
            </div>
            <div className={`w-8 h-4 rounded-full p-0.5 transition-colors ${deepSearchEnabled ? 'bg-emerald-500' : 'bg-forest-800'}`}>
              <div className={`w-3 h-3 rounded-full bg-white transition-transform ${deepSearchEnabled ? 'translate-x-4' : 'translate-x-0'}`} />
            </div>
          </div>
        </div>

        {/* Search Conversations Input */}
        <div className="px-3 pt-3">
          <div className="flex items-center gap-2 px-2.5 py-1.5 bg-forest-900/60 rounded-xl border border-forest-800/60 text-xs text-cream-200 focus-within:border-emerald-500/60">
            <Search className="w-3.5 h-3.5 text-cream-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search chat history..."
              className="bg-transparent text-xs text-cream-100 placeholder-cream-400/60 focus:outline-none w-full"
            />
          </div>
        </div>

        {/* Chat History List */}
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-1">
          <span className="px-2 text-[10px] uppercase font-bold tracking-wider text-cream-400/70 block mb-1">
            Conversations ({filteredSessions.length})
          </span>

          {filteredSessions.length === 0 ? (
            <div className="px-3 py-6 text-center text-xs text-cream-400/60">
              No chat history yet. Ask WanderWise to plan your next adventure!
            </div>
          ) : (
            filteredSessions.map((s) => (
              <div
                key={s.id}
                onClick={() => handleSelectSession(s.id)}
                className={`p-2.5 rounded-xl cursor-pointer text-xs font-medium transition-all flex items-center justify-between group ${sessionId === s.id
                  ? 'bg-forest-800 text-white font-semibold border-l-4 border-emerald-400 shadow-sm'
                  : 'text-cream-300/80 hover:bg-forest-800/50 hover:text-white'
                  }`}
              >
                <div className="flex items-center gap-2 overflow-hidden">
                  <MessageSquare className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span className="truncate">{s.title || 'Travel Planning'}</span>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(e, s.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 text-cream-400 hover:text-red-400 transition-opacity"
                  title="Delete chat"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>

        {/* Memory Inspector Drawer Trigger */}
        <div className="p-3 border-t border-forest-800/60">
          <button
            onClick={() => setShowMemoryModal(true)}
            className="w-full p-2 rounded-xl bg-forest-900/60 hover:bg-forest-800/60 border border-forest-800/80 text-[11px] text-cream-200 flex items-center justify-between transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className="text-sm">🧠</span>
              <span className="font-semibold">Context Memory State</span>
            </div>
            <span className="text-[10px] bg-emerald-950 text-emerald-300 font-bold px-1.5 py-0.5 rounded border border-emerald-800">
              {memoryState.destination ? 'Active' : 'Listening'}
            </span>
          </button>
        </div>

        {/* User Profile Footer */}
        <div className="p-3 border-t border-forest-800/60 flex items-center justify-between">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-forest-800 border border-emerald-400/40 flex items-center justify-center text-xs font-bold text-emerald-300 shrink-0">
              AS
            </div>
            <div className="overflow-hidden">
              <span className="font-bold text-xs text-white block truncate">Aarav Sharma</span>
              <span className="text-[10px] text-cream-400 block truncate">WanderWise Explorer</span>
            </div>
          </div>
        </div>
      </aside>

      {/* ======================================================== */}
      {/* 2. MAIN CHAT AREA (Pure Chatbot Experience)              */}
      {/* ======================================================== */}
      <main className="flex-1 flex flex-col h-screen min-w-0 bg-[#fcfaf7] relative">
        {/* Top Header Bar */}
        <header className="h-14 px-4 sm:px-6 bg-white/90 backdrop-blur-md border-b border-sand-200 flex items-center justify-between shrink-0 z-20">
          <div className="flex items-center gap-3">
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-sand-100 transition-colors"
                title="Open sidebar"
              >
                <PanelLeftOpen className="w-5 h-5 text-forest-800" />
              </button>
            )}

            <div className="flex items-center gap-2">
              <span className="font-serif font-bold text-slate-900 text-sm">
                WanderWise
              </span>
              <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Gemini 1.5 + DeepSearch
              </span>
            </div>
          </div>

          {/* Active Context Memory Chips in Header */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowMemoryModal(true)}
              className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-700 bg-sand-100 hover:bg-sand-200/80 px-2.5 py-1 rounded-full border border-sand-300 transition-colors"
              title="Click to view bot memory"
            >
              <span>📍 {memoryState.destination || 'Destination: Auto-detecting'}</span>
              <span className="text-slate-400">•</span>
              <span>⏱️ {memoryState.days || 3}d</span>
              <span className="text-slate-400">•</span>
              <span>💰 ₹{(memoryState.budget || 20000).toLocaleString()}</span>
            </button>

            {/* DeepSearch Quick Toggle in Header */}
            <button
              onClick={() => setDeepSearchEnabled(!deepSearchEnabled)}
              className={`px-2.5 py-1 rounded-full text-xs font-bold flex items-center gap-1 transition-all ${deepSearchEnabled
                ? 'bg-emerald-600 text-white shadow-soft-sm'
                : 'bg-sand-100 hover:bg-sand-200 text-slate-600 border border-sand-300'
                }`}
            >
              <Zap className="w-3 h-3 text-current" />
              <span className="text-[11px]">{deepSearchEnabled ? 'DeepSearch ON' : 'DeepSearch'}</span>
            </button>

            <button
              onClick={handleStartNewChat}
              className="p-1.5 rounded-lg text-slate-500 hover:text-forest-900 hover:bg-sand-200/80 transition-colors"
              title="Start fresh conversation"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Chat Feed Messages */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 md:px-12 py-6 space-y-6">
          <div className="max-w-3xl mx-auto space-y-6">

            {/* If NO messages yet, render ChatGPT/Claude style starter hero */}
            {messages.length === 0 ? (
              <div className="py-8 sm:py-14 text-center space-y-6">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-forest-800 to-emerald-500 mx-auto flex items-center justify-center shadow-soft-md">
                  <Compass className="w-9 h-9 text-white animate-pulse" />
                </div>

                <div className="space-y-2 max-w-md mx-auto">
                  <h2 className="font-serif text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                    Where would you like to travel?
                  </h2>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                    I am your autonomous travel planner chatbot. I remember your budget, companions, and preferences across our conversation, and generate live interactive itineraries and routing maps right here.
                  </p>
                </div>

                {/* 4 Interactive Starter Prompt Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left pt-2">
                  {PRESET_STARTER_CARDS.map((card, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleSendMessage(card.prompt, card.isDeepSearch)}
                      className="p-4 rounded-2xl bg-white hover:bg-forest-50/50 border border-sand-300/80 hover:border-forest-600/70 transition-all cursor-pointer shadow-soft-sm group space-y-1.5"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-xl">{card.icon}</span>
                        <h4 className="font-bold text-xs text-slate-900 group-hover:text-forest-800">
                          {card.title}
                        </h4>
                      </div>
                      <p className="text-[11px] text-slate-500 line-clamp-2">
                        {card.subtitle}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              // Active Conversation Messages
              messages.map((msg, idx) => (
                <div
                  key={msg.id || idx}
                  className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                >
                  {/* Message Sender Header */}
                  <div className="flex items-center gap-2 mb-1 px-1 text-[11px] text-slate-400 font-medium">
                    {msg.role === 'user' ? (
                      <span className="font-semibold text-slate-600">You</span>
                    ) : (
                      <span className="flex items-center gap-1.5 text-forest-800 font-bold">
                        <div className="w-4 h-4 rounded-full bg-forest-800 text-white flex items-center justify-center text-[9px]">
                          W
                        </div>
                        WanderWise AI
                      </span>
                    )}
                    {msg.is_deep_search && (
                      <span className="px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 text-[9px] font-bold">
                        ⚡ DEEPSEARCH
                      </span>
                    )}
                  </div>

                  {/* Message Bubble Container */}
                  <div
                    className={`p-4 sm:p-5 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-soft-sm max-w-[94%] sm:max-w-[88%] ${msg.role === 'user'
                      ? 'bg-forest-800 text-white rounded-tr-none'
                      : 'bg-white text-slate-800 border border-sand-300/80 rounded-tl-none'
                      }`}
                  >
                    {/* Text content with full Markdown rendering */}
                    <div className={`prose prose-sm max-w-none leading-relaxed ${msg.role === 'user' ? 'text-white' : 'text-slate-800'}`}>
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          table: ({ node, ...props }) => <div className="overflow-x-auto my-3"><table className="min-w-full divide-y divide-sand-300 text-xs border border-sand-200 rounded-xl shadow-sm overflow-hidden" {...props} /></div>,
                          thead: ({ node, ...props }) => <thead className="bg-sand-100/90 text-slate-800 font-bold border-b border-sand-300" {...props} />,
                          th: ({ node, ...props }) => <th className="px-3 py-2 text-left font-bold text-slate-900 border-b border-sand-300 bg-sand-100" {...props} />,
                          td: ({ node, ...props }) => <td className="px-3 py-2 border-b border-sand-200 text-slate-700" {...props} />,
                          tr: ({ node, ...props }) => <tr className="hover:bg-sand-50/70 transition-colors" {...props} />,
                          a: ({ node, ...props }) => <a className="text-emerald-700 hover:text-emerald-900 underline font-semibold transition-colors" target="_blank" rel="noopener noreferrer" {...props} />,
                          h1: ({ node, ...props }) => <h1 className="text-base font-bold text-slate-900 mt-3 mb-1.5 font-serif" {...props} />,
                          h2: ({ node, ...props }) => <h2 className="text-sm font-bold text-slate-900 mt-2.5 mb-1 font-serif" {...props} />,
                          h3: ({ node, ...props }) => <h3 className="text-xs font-bold text-forest-800 uppercase tracking-wider mt-2 mb-1" {...props} />,
                          ul: ({ node, ...props }) => <ul className="list-disc list-outside pl-4 space-y-1 my-2 text-inherit" {...props} />,
                          ol: ({ node, ...props }) => <ol className="list-decimal list-outside pl-4 space-y-1 my-2 text-inherit" {...props} />,
                          li: ({ node, ...props }) => <li className="text-xs sm:text-sm text-inherit pl-0.5" {...props} />,
                          p: ({ node, ...props }) => <p className="mb-2 last:mb-0 leading-relaxed text-inherit" {...props} />,
                          blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-emerald-600 pl-3 italic my-2 text-slate-600 bg-sand-50/80 py-1.5 rounded-r text-xs sm:text-sm" {...props} />,
                          strong: ({ node, ...props }) => <strong className={`font-bold ${msg.role === 'user' ? 'text-white' : 'text-slate-900'}`} {...props} />
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>

                    {/* ======================================================== */}
                    {/* A. DEEPSEARCH DOSSIER EMBED                               */}
                    {/* ======================================================== */}
                    {msg.structured_type === 'deep_search_card' && msg.structured_data && (
                      <div className="mt-4 p-4 rounded-2xl bg-forest-950 text-cream-100 border border-forest-800 space-y-3.5 shadow-md">
                        <div className="flex items-center justify-between border-b border-forest-800/80 pb-2.5">
                          <div className="flex items-center gap-2">
                            <Zap className="w-4 h-4 text-emerald-400 animate-pulse" />
                            <h4 className="font-serif font-bold text-sm text-white">
                              DeepSearch Dossier: {msg.structured_data.destination}
                            </h4>
                          </div>
                          <span className="px-2 py-0.5 rounded-full bg-emerald-900/60 text-emerald-300 text-[10px] font-bold border border-emerald-600">
                            Verified Terrain & Satellite Telemetry
                          </span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                          <div className="p-3 rounded-xl bg-forest-900/80 border border-forest-800/80 space-y-1">
                            <span className="text-[10px] font-bold text-sand-300 uppercase block">
                              🏔️ Altitude & Terrain
                            </span>
                            <p className="text-[11px] text-cream-200">{msg.structured_data.altitude_terrain}</p>
                          </div>
                          <div className="p-3 rounded-xl bg-forest-900/80 border border-forest-800/80 space-y-1">
                            <span className="text-[10px] font-bold text-sand-300 uppercase block">
                              📸 Prime Golden-Hour Windows
                            </span>
                            <p className="text-[11px] text-cream-200">
                              {msg.structured_data.best_photography_windows?.[0]?.location} ({msg.structured_data.best_photography_windows?.[0]?.time})
                            </p>
                          </div>
                        </div>

                        {/* Hidden Offbeat Gems */}
                        <div className="p-3 rounded-xl bg-forest-900/60 border border-forest-800/80 text-[11px] space-y-1.5">
                          <span className="font-bold text-sand-300 block">💎 Secret Offbeat Gems:</span>
                          <p className="text-cream-200 font-medium">
                            {msg.structured_data.offbeat_hidden_gems?.[0]?.name} — {msg.structured_data.offbeat_hidden_gems?.[0]?.desc}
                          </p>
                        </div>

                        <div className="flex items-center justify-between text-[10px] text-cream-400 pt-1 border-t border-forest-800/80">
                          <span>Verified via OpenStreetMap & Open-Meteo</span>
                          <button
                            onClick={() => handleAction({ action: 'generate_itinerary', destination: msg.structured_data.destination })}
                            className="font-bold text-emerald-400 hover:text-white flex items-center gap-1 transition-colors"
                          >
                            Build Itinerary from Dossier →
                          </button>
                        </div>
                      </div>
                    )}

                    {/* ======================================================== */}
                    {/* B. MULTI-TAB IN-CHAT ITINERARY & ROUTE MAP CARD           */}
                    {/* ======================================================== */}
                    {msg.structured_type === 'itinerary_preview' && msg.structured_data?.itinerary && (
                      <div className="mt-4 pt-3 border-t border-sand-200 space-y-3">
                        {/* Tab Switcher inside the Chat Message */}
                        <div className="flex items-center gap-1 bg-sand-100 p-1 rounded-xl border border-sand-300 text-xs font-semibold">
                          <button
                            onClick={() => setActiveTabByMsgId(prev => ({ ...prev, [msg.id]: 'schedule' }))}
                            className={`flex-1 py-1.5 px-2 rounded-lg transition-all flex items-center justify-center gap-1.5 ${(activeTabByMsgId[msg.id] || 'schedule') === 'schedule'
                              ? 'bg-white text-forest-900 shadow-sm font-bold'
                              : 'text-slate-600 hover:text-slate-900'
                              }`}
                          >
                            <Calendar className="w-3.5 h-3.5" />
                            <span>Day Schedule</span>
                          </button>
                          <button
                            onClick={() => setActiveTabByMsgId(prev => ({ ...prev, [msg.id]: 'map' }))}
                            className={`flex-1 py-1.5 px-2 rounded-lg transition-all flex items-center justify-center gap-1.5 ${activeTabByMsgId[msg.id] === 'map'
                              ? 'bg-white text-forest-900 shadow-sm font-bold'
                              : 'text-slate-600 hover:text-slate-900'
                              }`}
                          >
                            <MapPin className="w-3.5 h-3.5" />
                            <span>Interactive Route Map</span>
                          </button>
                          <button
                            onClick={() => setActiveTabByMsgId(prev => ({ ...prev, [msg.id]: 'budget' }))}
                            className={`flex-1 py-1.5 px-2 rounded-lg transition-all flex items-center justify-center gap-1.5 ${activeTabByMsgId[msg.id] === 'budget'
                              ? 'bg-white text-forest-900 shadow-sm font-bold'
                              : 'text-slate-600 hover:text-slate-900'
                              }`}
                          >
                            <Wallet className="w-3.5 h-3.5" />
                            <span>Budget</span>
                          </button>
                        </div>

                        {/* Tab 1: Day Schedule */}
                        {(activeTabByMsgId[msg.id] || 'schedule') === 'schedule' && (
                          <div className="space-y-3">
                            {msg.structured_data.itinerary.map((day) => (
                              <div key={day.day_number} className="p-3.5 rounded-2xl bg-cream-50 border border-sand-300 space-y-2">
                                <div className="flex items-center justify-between">
                                  <span className="font-bold text-xs text-forest-900">{day.title}</span>
                                  <span className="text-[10px] text-slate-500 font-semibold">{day.theme}</span>
                                </div>
                                <div className="space-y-1.5 text-xs text-slate-700">
                                  {day.activities?.map((act, i) => (
                                    <div key={i} className="flex items-start justify-between gap-2 p-2 rounded-xl bg-white border border-sand-200">
                                      <div>
                                        <span className="font-semibold text-slate-900 block">{act.time_str} • {act.title}</span>
                                        <span className="text-[11px] text-slate-500">{act.location_name}</span>
                                      </div>
                                      <span className="font-bold text-forest-800 shrink-0">₹{act.estimated_cost}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Tab 2: Embedded Leaflet Map */}
                        {activeTabByMsgId[msg.id] === 'map' && (
                          <div className="space-y-2">
                            <span className="text-[11px] text-slate-500 block">
                              📍 Click markers to preview stops, timings, and road curvature routes:
                            </span>
                            <InteractiveMap
                              activities={msg.structured_data.itinerary.flatMap(d => (d.activities || []).map(a => ({ ...a, day_number: d.day_number })))}
                              height="380px"
                            />
                          </div>
                        )}

                        {/* Tab 3: Budget Breakdown in chat */}
                        {activeTabByMsgId[msg.id] === 'budget' && (
                          <div className="p-3.5 rounded-2xl bg-cream-50 border border-sand-300 space-y-3">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-xs text-slate-800">Trip Budget Summary</span>
                              <span className="text-xs font-bold text-forest-800">
                                Total: ₹{(memoryState.budget || 20000).toLocaleString()}
                              </span>
                            </div>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
                              <div className="p-2 rounded-xl bg-white border border-sand-200">
                                <span className="text-[10px] text-slate-500 block">Stay</span>
                                <span className="font-bold text-slate-800">₹{(memoryState.budget * 0.35 || 7000).toLocaleString()}</span>
                              </div>
                              <div className="p-2 rounded-xl bg-white border border-sand-200">
                                <span className="text-[10px] text-slate-500 block">Food</span>
                                <span className="font-bold text-slate-800">₹{(memoryState.budget * 0.25 || 5000).toLocaleString()}</span>
                              </div>
                              <div className="p-2 rounded-xl bg-white border border-sand-200">
                                <span className="text-[10px] text-slate-500 block">Activities</span>
                                <span className="font-bold text-slate-800">₹{(memoryState.budget * 0.25 || 5000).toLocaleString()}</span>
                              </div>
                              <div className="p-2 rounded-xl bg-white border border-sand-200">
                                <span className="text-[10px] text-slate-500 block">Per Person</span>
                                <span className="font-bold text-forest-700">
                                  ₹{Math.round((memoryState.budget || 20000) / (memoryState.travellers || 2)).toLocaleString()}
                                </span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* ======================================================== */}
                    {/* C. DESTINATION RECOMMENDATION CARDS EMBED                 */}
                    {/* ======================================================== */}
                    {msg.structured_type === 'destination_list' && msg.structured_data?.destinations && (
                      <div className="mt-4 pt-3 border-t border-sand-200 space-y-3">
                        <span className="text-xs font-bold text-slate-700 block">
                          AI-Matched Destinations for you:
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          {msg.structured_data.destinations.map((dest) => (
                            <div
                              key={dest.id}
                              onClick={() => handleAction({ action: 'generate_itinerary', destination: dest.name })}
                              className="group cursor-pointer rounded-2xl bg-cream-50 hover:bg-white border border-sand-200 hover:border-forest-600 transition-all p-3 space-y-2 shadow-sm"
                            >
                              <img
                                src={dest.image_url}
                                alt={dest.name}
                                className="w-full h-28 rounded-xl object-cover"
                              />
                              <div className="flex items-center justify-between">
                                <h5 className="font-bold text-xs text-slate-900 group-hover:text-forest-800">{dest.name}</h5>
                                <span className="text-[10px] font-bold text-forest-700 bg-forest-50 px-1.5 py-0.5 rounded">
                                  {dest.match_score}% Match
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-500 line-clamp-1">{dest.why_selected}</p>
                              <div className="flex items-center justify-between text-[10px] text-slate-600 pt-1 border-t border-sand-100 font-semibold">
                                <span>₹{dest.estimated_daily_budget}/day</span>
                                <span className="text-forest-700 font-bold">Plan Trip →</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* ======================================================== */}
                    {/* D. TRANSIT & WORLDWIDE TRAVEL COST CARD EMBED            */}
                    {/* ======================================================== */}
                    {msg.structured_type === 'transit_cost_card' && msg.structured_data?.options && (
                      <div className="mt-4 pt-3 border-t border-sand-200 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-base">🧭</span>
                            <h4 className="font-bold text-xs sm:text-sm text-slate-900 font-serif">
                              Transit & Travel Costs: {msg.structured_data.origin} ➔ {msg.structured_data.destination}
                            </h4>
                          </div>
                          <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full border border-emerald-300">
                            Live Fare Benchmarks
                          </span>
                        </div>

                        {/* Transit Options Grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                          {msg.structured_data.options.map((opt, oIdx) => (
                            <div
                              key={oIdx}
                              className="p-3.5 rounded-2xl bg-cream-50/70 hover:bg-white border border-sand-300/80 hover:border-forest-600/70 transition-all shadow-sm space-y-2 group"
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <span className="text-xl">{opt.icon}</span>
                                  <div>
                                    <span className="font-bold text-xs text-slate-900 block group-hover:text-forest-800">
                                      {opt.label}
                                    </span>
                                    <span className="text-[10px] text-slate-500 block truncate max-w-[150px]">
                                      {opt.carrier}
                                    </span>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <span className="font-bold text-xs text-forest-800 block">
                                    {opt.price_inr_range}
                                  </span>
                                  <span className="text-[10px] text-slate-500 block">
                                    {opt.price_usd_range}
                                  </span>
                                </div>
                              </div>

                              <div className="grid grid-cols-2 gap-1.5 py-1 px-2 rounded-xl bg-white/80 border border-sand-200 text-[10px] text-slate-600">
                                <div>
                                  <span className="text-slate-400 block">Duration</span>
                                  <span className="font-semibold text-slate-800">{opt.duration}</span>
                                </div>
                                <div>
                                  <span className="text-slate-400 block">Frequency</span>
                                  <span className="font-semibold text-slate-800">{opt.frequency}</span>
                                </div>
                              </div>

                              <div className="flex items-center justify-between pt-1">
                                <span className="text-[10px] text-emerald-700 font-medium truncate max-w-[140px]">
                                  🌱 {opt.eco_rating}
                                </span>
                                {opt.booking_url && (
                                  <a
                                    href={opt.booking_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-[10px] font-bold text-white bg-forest-800 hover:bg-forest-900 px-2.5 py-1 rounded-lg flex items-center gap-1 transition-all shadow-xs shrink-0"
                                  >
                                    <span>Live Fares</span>
                                    <span>↗</span>
                                  </a>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Live Booking Portals Toolbar */}
                        {msg.structured_data.live_links && (
                          <div className="p-2.5 rounded-xl bg-sand-100/70 border border-sand-200 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-600">
                            <span className="font-semibold text-slate-700">Check Live Availability & Book:</span>
                            <div className="flex items-center gap-2">
                              {msg.structured_data.live_links.google_flights && (
                                <a
                                  href={msg.structured_data.live_links.google_flights}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-emerald-700 hover:text-emerald-900 font-bold underline"
                                >
                                  Google Flights ↗
                                </a>
                              )}
                              <span>•</span>
                              <a
                                href="https://www.skyscanner.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-emerald-700 hover:text-emerald-900 font-bold underline"
                              >
                                Skyscanner ↗
                              </a>
                              <span>•</span>
                              <a
                                href="https://www.thetrainline.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-emerald-700 hover:text-emerald-900 font-bold underline"
                              >
                                Trainline ↗
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* ======================================================== */}
                    {/* E. WORLDWIDE HOTEL & RESORT SUGGESTIONS EMBED             */}
                    {/* ======================================================== */}
                    {msg.structured_type === 'hotel_suggestion_card' && msg.structured_data?.hotels && (
                      <div className="mt-4 pt-3 border-t border-sand-200 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-base">🏨</span>
                            <h4 className="font-bold text-xs sm:text-sm text-slate-900 font-serif">
                              Hotel & Stay Recommendations: {msg.structured_data.clean_destination || msg.structured_data.destination}
                            </h4>
                          </div>
                          <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full border border-emerald-300">
                            Live Rate Benchmarks
                          </span>
                        </div>

                        {/* Hotel Cards Grid */}
                        <div className="grid grid-cols-1 gap-3">
                          {msg.structured_data.hotels.map((h, hIdx) => (
                            <div
                              key={hIdx}
                              className="p-3.5 rounded-2xl bg-cream-50/70 hover:bg-white border border-sand-300/80 hover:border-forest-600/70 transition-all shadow-sm space-y-2 group"
                            >
                              <div className="flex items-start justify-between gap-2">
                                <div>
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
                                      {h.tier}
                                    </span>
                                    <span className="text-[10px] font-medium text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                                      {h.badge}
                                    </span>
                                  </div>
                                  <h5 className="font-bold text-sm text-slate-900 group-hover:text-forest-800 transition-colors">
                                    {h.name}
                                  </h5>
                                  <div className="flex items-center gap-1.5 text-[11px] text-slate-500 mt-0.5">
                                    <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                                    <span>{h.neighborhood}</span>
                                  </div>
                                </div>
                                <div className="text-right shrink-0">
                                  <span className="font-bold text-sm text-forest-800 block">
                                    {h.price_inr_range}
                                  </span>
                                  <span className="text-[10px] text-slate-500 block">
                                    {h.price_usd_range}
                                  </span>
                                  <div className="flex items-center justify-end gap-1 mt-1">
                                    <span className="text-amber-500 text-xs font-bold">★</span>
                                    <span className="text-[11px] font-bold text-slate-800">{h.rating}</span>
                                    <span className="text-[10px] text-slate-400">({h.reviews_count})</span>
                                  </div>
                                </div>
                              </div>

                              <p className="text-xs text-slate-600 leading-relaxed bg-white/70 p-2 rounded-xl border border-sand-200">
                                {h.why_stay}
                              </p>

                              {/* Amenities Chips */}
                              {h.amenities && (
                                <div className="flex flex-wrap gap-1.5 pt-0.5">
                                  {h.amenities.map((am, amIdx) => (
                                    <span
                                      key={amIdx}
                                      className="text-[10px] font-medium text-slate-600 bg-sand-100 px-2 py-0.5 rounded-md border border-sand-200/80"
                                    >
                                      ✓ {am}
                                    </span>
                                  ))}
                                </div>
                              )}

                              {/* Booking Link Action */}
                              <div className="flex items-center justify-between pt-1.5 border-t border-sand-200/80">
                                <span className="text-[10px] text-slate-500 italic">
                                  Free cancellation available on selected rooms
                                </span>
                                <a
                                  href={h.booking_url || (msg.structured_data.live_booking_links && msg.structured_data.live_booking_links.booking_com)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-[11px] font-bold text-white bg-forest-800 hover:bg-forest-900 px-3 py-1.5 rounded-xl flex items-center gap-1.5 transition-all shadow-xs shrink-0"
                                >
                                  <span>View Live Deals</span>
                                  <span>↗</span>
                                </a>
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Live Booking Portals Toolbar */}
                        {msg.structured_data.live_booking_links && (
                          <div className="p-2.5 rounded-xl bg-sand-100/70 border border-sand-200 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-600">
                            <span className="font-semibold text-slate-700">Compare & Book Live Stays:</span>
                            <div className="flex items-center gap-2">
                              <a
                                href={msg.structured_data.live_booking_links.booking_com}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-700 hover:text-blue-900 font-bold underline"
                              >
                                Booking.com ↗
                              </a>
                              <span>•</span>
                              <a
                                href={msg.structured_data.live_booking_links.google_hotels}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-slate-800 hover:text-black font-bold underline"
                              >
                                Google Hotels ↗
                              </a>
                              <span>•</span>
                              <a
                                href={msg.structured_data.live_booking_links.agoda}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-indigo-700 hover:text-indigo-900 font-bold underline"
                              >
                                Agoda ↗
                              </a>
                              <span>•</span>
                              <a
                                href={msg.structured_data.live_booking_links.airbnb}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-rose-600 hover:text-rose-800 font-bold underline"
                              >
                                Airbnb ↗
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Suggested Next Action Chips */}
                  {msg.suggested_actions && msg.suggested_actions.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2.5 max-w-[94%] sm:max-w-[88%]">
                      {msg.suggested_actions.map((act, aIdx) => (
                        <button
                          key={aIdx}
                          onClick={() => handleAction(act)}
                          className="px-3 py-1.5 rounded-full bg-white hover:bg-forest-50 border border-sand-300 hover:border-forest-600 text-xs font-semibold text-forest-900 transition-all shadow-soft-sm flex items-center gap-1.5 active:scale-95"
                        >
                          <span>{act.label}</span>
                          <ArrowRight className="w-3 h-3 text-slate-400" />
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}

            {/* ChatGPT-style Typing Indicator */}
            {loading && (
              <div className="flex flex-col items-start">
                <div className="flex items-center gap-1.5 mb-1 px-1 text-[11px] text-forest-800 font-bold">
                  <div className="w-4 h-4 rounded-full bg-forest-800 text-white flex items-center justify-center text-[9px]">
                    W
                  </div>
                  <span>WanderWise AI</span>
                  <span className="text-[10px] text-emerald-600 font-semibold animate-pulse">
                    {deepSearchEnabled ? '⚡ DeepSearching...' : 'thinking...'}
                  </span>
                </div>
                <div className="p-3.5 px-4 rounded-2xl bg-white border border-sand-300/80 rounded-tl-none shadow-soft-sm flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-forest-700 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 rounded-full bg-forest-700 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 rounded-full bg-forest-700 animate-bounce" style={{ animationDelay: '300ms' }} />
                  <span className="text-xs text-slate-500 font-medium ml-1">
                    {deepSearchEnabled
                      ? 'Analyzing terrain topology, golden hours & hidden gems...'
                      : 'Consulting global travel intelligence...'}
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* ======================================================== */}
        {/* 3. FLOATING PROMPT INPUT DOCK (ChatGPT / Claude Style)    */}
        {/* ======================================================== */}
        <div className="p-3 sm:p-4 bg-white/90 backdrop-blur-md border-t border-sand-200 shrink-0">
          <div className="max-w-3xl mx-auto space-y-2">

            {/* Quick Prompt Carousel */}
            <div className="flex gap-2 overflow-x-auto no-scrollbar pb-0.5">
              {QUICK_MOOD_PROMPTS.map((promptText, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(promptText)}
                  className="whitespace-nowrap px-3 py-1 rounded-full bg-sand-100 hover:bg-sand-200/80 border border-sand-300 text-[11px] font-medium text-slate-700 transition-colors"
                >
                  {promptText}
                </button>
              ))}
            </div>

            {/* Input Form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2 bg-[#fcfaf7] p-2 rounded-2xl border border-sand-300 focus-within:ring-2 focus-within:ring-forest-600 focus-within:bg-white transition-all shadow-soft-sm"
            >
              {/* DeepSearch Switcher Pill inside input */}
              <button
                type="button"
                onClick={() => setDeepSearchEnabled(!deepSearchEnabled)}
                className={`px-3 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all shrink-0 ${deepSearchEnabled
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'bg-white hover:bg-sand-100 text-slate-700 border border-sand-300'
                  }`}
                title="Toggle DeepSearch Mode"
              >
                <Zap className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">DeepSearch</span>
              </button>

              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={
                  deepSearchEnabled
                    ? "DeepSearch active: Ask for offbeat trails, road advisories, golden hour..."
                    : "Message WanderWise... (e.g. 4 days in Munnar with ₹15,000 for 3 friends)"
                }
                className="flex-1 px-2 py-2 bg-transparent text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
              />

              <button
                type="submit"
                disabled={!inputMessage.trim() || loading}
                className="p-2.5 sm:p-3 rounded-xl bg-forest-800 hover:bg-forest-700 disabled:opacity-40 text-white transition-all shadow-sm shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>

            <p className="text-[10px] text-center text-slate-400 font-medium">
              WanderWise AI retains multi-turn memory across conversations. Powered by Gemini & Open-Meteo.
            </p>
          </div>
        </div>

        {/* ======================================================== */}
        {/* CONTEXT MEMORY STATE MODAL                               */}
        {/* ======================================================== */}
        {showMemoryModal && (
          <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-soft-xl border border-sand-200 space-y-4">
              <div className="flex items-center justify-between border-b border-sand-200 pb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xl">🧠</span>
                  <h3 className="font-serif font-bold text-base text-slate-900">
                    Active Context Memory
                  </h3>
                </div>
                <button
                  onClick={() => setShowMemoryModal(false)}
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-800"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <p className="text-xs text-slate-600">
                WanderWise retains your travel preferences across conversation turns so you never have to re-enter them:
              </p>

              <div className="p-4 rounded-2xl bg-cream-50 border border-sand-300 space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-sand-200">
                  <span className="text-slate-500">Destination:</span>
                  <span className="font-bold text-forest-900">{memoryState.destination || 'Not yet locked in'}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-sand-200">
                  <span className="text-slate-500">Trip Duration:</span>
                  <span className="font-bold text-slate-800">{memoryState.days || 3} Days</span>
                </div>
                <div className="flex justify-between py-1 border-b border-sand-200">
                  <span className="text-slate-500">Total Budget:</span>
                  <span className="font-bold text-forest-800">₹{(memoryState.budget || 20000).toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-sand-200">
                  <span className="text-slate-500">Travellers Count:</span>
                  <span className="font-bold text-slate-800">{memoryState.travellers || 2} People</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">DeepSearch:</span>
                  <span className="font-bold text-emerald-600">{deepSearchEnabled ? 'Enabled' : 'Disabled'}</span>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => {
                    handleStartNewChat();
                    setShowMemoryModal(false);
                  }}
                  className="flex-1 py-2 px-3 rounded-xl border border-red-200 text-red-600 hover:bg-red-50 text-xs font-bold transition-colors"
                >
                  Clear Memory
                </button>
                <button
                  onClick={() => setShowMemoryModal(false)}
                  className="flex-1 py-2 px-3 rounded-xl bg-forest-800 hover:bg-forest-700 text-white text-xs font-bold transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* What-If Simulator Modal */}
        <WhatIfSimulatorModal
          trip={simulatorTrip}
          isOpen={showSimulator}
          onClose={() => setShowSimulator(false)}
          onApplyChanges={(simRes) => {
            setMemoryState(prev => ({
              ...prev,
              days: simRes.new_duration_days,
              budget: simRes.new_cost,
              travellers: simRes.new_travellers
            }));
            handleSendMessage(`Applied What-If changes: updated to ${simRes.new_duration_days} days, ${simRes.new_travellers} travellers, and ₹${simRes.new_cost} total cost.`);
          }}
        />
      </main>
    </div>
  );
}
