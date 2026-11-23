import React, { useState, useEffect, useRef } from 'react';
import { 
  X, Send, Sparkles, Compass, MapPin, Calendar, 
  Wallet, RefreshCw, ChevronRight, CheckCircle2, MessageSquare
} from 'lucide-react';
import { useTrip } from '../../context/TripContext';
import { api } from '../../services/api';
import { useNavigate } from 'react-router-dom';

const DEFAULT_PROMPTS = [
  "I want to travel somewhere peaceful for 4 days.",
  "My budget is ₹15,000 and I am travelling with 3 friends.",
  "I like mountains, coffee shops and scenic sunsets.",
  "Make day 2 less hectic with relaxed cafes.",
  "What if we extend the trip by one day?"
];

export default function ChatbotDrawer() {
  const { isChatOpen, setIsChatOpen, prefilledPrompt, setPrefilledPrompt, activeTrip, refreshTrips } = useTrip();
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hello Aarav! I'm WanderWise AI, your personal travel copilot. Where would you like to explore, or what kind of vibe are you dreaming of?",
      structured_type: null,
      structured_data: null
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (prefilledPrompt) {
      setInputMessage(prefilledPrompt);
      setPrefilledPrompt('');
    }
  }, [prefilledPrompt]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (textToSend = null) => {
    const text = textToSend || inputMessage.trim();
    if (!text || loading) return;

    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: text
    };
    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await api.sendChatMessage({
        message: text,
        session_id: sessionId,
        trip_id: activeTrip?.id
      });

      if (response.session_id) {
        setSessionId(response.session_id);
      }

      setMessages(prev => [...prev, {
        id: response.message.id || Date.now() + 1,
        role: 'assistant',
        content: response.message.content,
        structured_type: response.message.structured_type,
        structured_data: response.message.structured_data,
        suggested_actions: response.suggested_actions
      }]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: "I hit a brief connection hiccup reaching the live travel servers. Please verify the backend is running and ask again!",
        structured_type: null
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (actionItem) => {
    if (actionItem.action === 'prompt') {
      handleSendMessage(actionItem.text);
    } else if (actionItem.action === 'generate_itinerary') {
      handleSendMessage(`Create a full ${actionItem.days || 5}-day itinerary for ${actionItem.destination}`);
    } else if (actionItem.action === 'save_itinerary' && actionItem.itinerary) {
      setLoading(true);
      try {
        const daysLen = actionItem.itinerary?.length || 5;
        const now = new Date();
        const startStr = now.toISOString().split('T')[0];
        const endD = new Date(now.getTime() + daysLen * 86400000);
        const endStr = endD.toISOString().split('T')[0];
        const newTrip = await api.createTrip({
          title: `Trip to ${activeTrip?.destination || 'India'}`,
          destination: activeTrip?.destination || 'India',
          start_date: startStr,
          end_date: endStr,
          travellers_count: 2,
          total_budget: 20000.0,
          travel_style: 'Scenic Exploration'
        });
        await refreshTrips();
        setIsChatOpen(false);
        navigate(`/trips/${newTrip.id}`);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    } else if (actionItem.action === 'view_itinerary' && activeTrip) {
      setIsChatOpen(false);
      navigate(`/trips/${activeTrip.id}`);
    } else if (actionItem.action === 'open_simulator' && activeTrip) {
      setIsChatOpen(false);
      navigate(`/trips/${activeTrip.id}?tab=simulator`);
    } else {
      handleSendMessage(actionItem.label);
    }
  };

  if (!isChatOpen) {
    return (
      <button
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-20 lg:bottom-8 right-6 z-40 p-4 rounded-full bg-forest-800 hover:bg-forest-700 text-white shadow-soft-xl hover:scale-105 active:scale-95 transition-all flex items-center gap-2.5 border-2 border-sand-300 group"
      >
        <Sparkles className="w-5 h-5 text-sand-300 animate-spin" style={{ animationDuration: '8s' }} />
        <span className="font-semibold text-xs tracking-wide pr-1 hidden sm:inline">Ask Travel AI</span>
      </button>
    );
  }

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[480px] bg-cream-100 shadow-2xl z-50 flex flex-col border-l border-sand-300 animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="p-4 bg-forest-900 text-cream-100 flex items-center justify-between border-b border-forest-800 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-forest-700/80 border border-sand-400/40 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-sand-300" />
          </div>
          <div>
            <h3 className="font-serif font-bold text-sm text-white">WanderWise Copilot</h3>
            <span className="text-[10px] text-sand-300 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              Live Contextual Travel AI
            </span>
          </div>
        </div>
        <button
          onClick={() => setIsChatOpen(false)}
          className="p-1.5 rounded-lg hover:bg-forest-800 text-cream-300 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={msg.id || i}
            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            {/* Message Bubble */}
            <div
              className={`max-w-[88%] p-3.5 rounded-2xl text-xs leading-relaxed shadow-soft-sm ${
                msg.role === 'user'
                  ? 'bg-forest-800 text-white rounded-br-none'
                  : 'bg-white text-slate-800 border border-sand-200 rounded-bl-none'
              }`}
            >
              <p className="whitespace-pre-line">{msg.content}</p>

              {/* Render Structured Destination Cards */}
              {msg.structured_type === 'destination_list' && msg.structured_data?.destinations && (
                <div className="mt-3 space-y-2.5 pt-2 border-t border-sand-200">
                  {msg.structured_data.destinations.map((dest) => (
                    <div
                      key={dest.id}
                      onClick={() => handleAction({ action: 'generate_itinerary', destination: dest.name })}
                      className="group cursor-pointer p-2.5 rounded-xl bg-cream-50 hover:bg-white border border-sand-200 hover:border-forest-600 transition-all shadow-sm flex items-center gap-3"
                    >
                      <img
                        src={dest.image_url}
                        alt={dest.name}
                        className="w-16 h-16 rounded-lg object-cover shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h4 className="font-bold text-slate-900 text-xs truncate group-hover:text-forest-700">{dest.name}</h4>
                          <span className="text-[10px] font-bold text-forest-700 bg-forest-50 px-1.5 py-0.5 rounded">
                            {dest.match_score}% Match
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">{dest.why_selected}</p>
                        <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-600 font-medium">
                          <span>₹{dest.estimated_daily_budget}/day</span>
                          <span>•</span>
                          <span>Best: {dest.best_season}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Render Structured Itinerary Preview Card */}
              {msg.structured_type === 'itinerary_preview' && msg.structured_data?.itinerary && (
                <div className="mt-3 p-3 rounded-xl bg-forest-900 text-cream-100 border border-forest-700 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-serif font-bold text-xs text-white">
                      {msg.structured_data.destination}
                    </span>
                    <span className="text-[10px] text-sand-300 font-semibold">
                      {msg.structured_data.days_count} Days
                    </span>
                  </div>
                  <div className="space-y-1.5 text-[11px] max-h-72 overflow-y-auto pr-1">
                    {msg.structured_data.itinerary.map((day) => (
                      <div key={day.day_number} className="p-2 rounded-lg bg-forest-800/80 border border-forest-700/60">
                        <span className="font-semibold text-sand-300 block">{day.title}</span>
                        <span className="text-[10px] text-cream-300/80">{day.theme}</span>
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={() => handleAction({ action: 'save_itinerary', itinerary: msg.structured_data.itinerary })}
                    className="w-full py-2 rounded-lg bg-sand-400 hover:bg-sand-300 text-forest-950 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors mt-2"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Save & Open Interactive Plan
                  </button>
                </div>
              )}

              {/* Render Budget Summary Card */}
              {msg.structured_type === 'budget_summary' && msg.structured_data && (
                <div className="mt-3 p-3 rounded-xl bg-cream-50 border border-sand-300 text-slate-800 space-y-2">
                  <div className="flex items-center justify-between font-bold text-xs">
                    <span>Estimated Total</span>
                    <span className="text-forest-700 font-extrabold text-sm">₹{msg.structured_data.total_budget?.toLocaleString()}</span>
                  </div>
                  <div className="space-y-1 text-[11px]">
                    {msg.structured_data.breakdown?.map((b) => (
                      <div key={b.category} className="flex items-center justify-between text-slate-600">
                        <span>{b.category}</span>
                        <span className="font-semibold text-slate-800">₹{Math.round(b.amount).toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Suggested Actions Chips */}
            {msg.suggested_actions && (
              <div className="flex flex-wrap gap-1.5 mt-2 max-w-[90%]">
                {msg.suggested_actions.map((act, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAction(act)}
                    className="px-2.5 py-1 rounded-full bg-white hover:bg-forest-50 border border-sand-300 hover:border-forest-600 text-[11px] font-medium text-forest-900 transition-colors shadow-soft-sm flex items-center gap-1"
                  >
                    <span>{act.label}</span>
                    <ChevronRight className="w-3 h-3 text-slate-400" />
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 p-3 rounded-2xl bg-white border border-sand-200 text-xs text-slate-500 w-fit">
            <Sparkles className="w-3.5 h-3.5 text-forest-700 animate-spin" />
            <span>WanderWise AI is thinking and structuring your trip...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Chips */}
      <div className="px-4 py-2 border-t border-sand-200/60 bg-cream-50/70 overflow-x-auto flex gap-1.5 shrink-0 no-scrollbar">
        {DEFAULT_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(prompt)}
            className="whitespace-nowrap px-2.5 py-1 rounded-full bg-white hover:bg-cream-200 border border-sand-300 text-[10px] font-medium text-slate-700 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <div className="p-3 bg-white border-t border-sand-200 shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask about places, budgets, weather, changes..."
            className="flex-1 px-3.5 py-2.5 rounded-full bg-cream-100 border border-sand-300 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-forest-600 focus:bg-white transition-all"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || loading}
            className="p-2.5 rounded-full bg-forest-800 hover:bg-forest-700 disabled:opacity-40 text-white transition-all shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}

