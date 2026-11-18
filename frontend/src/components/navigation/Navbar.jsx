import React, { useState } from 'react';
import { Search, Bell, Sparkles, Compass, MapPin } from 'lucide-react';
import { useTrip } from '../../context/TripContext';
import { useNavigate } from 'react-router-dom';

export default function Navbar() {
  const { openChatWithPrompt } = useTrip();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    { id: 1, title: 'Live Weather Alert', desc: 'Mild afternoon rain in Munnar. Indoor cultural schedule suggested.', time: '10m ago', unread: true },
    { id: 2, title: 'Group Expense Logged', desc: 'Rohan added ₹1,400 for Lockhart High-Grown Tea.', time: '2h ago', unread: true },
    { id: 3, title: 'Trip Milestone', desc: 'Packing checklist is 85% completed!', time: '1d ago', unread: false }
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/explore?search=${encodeURIComponent(searchTerm.trim())}`);
      setSearchTerm('');
    }
  };

  return (
    <header className="sticky top-0 z-20 bg-cream-100/90 backdrop-blur-md border-b border-sand-200/60 px-4 lg:px-8 py-3.5 flex items-center justify-between transition-all">
      {/* Mobile Brand / Search */}
      <div className="flex items-center gap-3">
        <div className="lg:hidden flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-forest-800 flex items-center justify-center text-white">
            <Compass className="w-5 h-5 text-sand-300" />
          </div>
          <span className="font-serif font-bold text-forest-900 text-lg">WanderWise</span>
        </div>

        {/* Global Search Bar */}
        <form onSubmit={handleSearch} className="hidden sm:flex items-center relative max-w-md w-72 lg:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search destinations, beaches, mountains..."
            className="w-full pl-9 pr-4 py-2 rounded-full bg-cream-200/80 border border-sand-300/80 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-forest-600 focus:bg-white transition-all shadow-soft-sm"
          />
        </form>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-2.5 sm:gap-3.5">
        {/* Quick AI Copilot Button */}
        <button
          onClick={() => openChatWithPrompt()}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-gradient-to-r from-forest-800 to-forest-700 hover:from-forest-700 hover:to-forest-600 text-cream-100 text-xs font-semibold shadow-soft-sm transition-all hover:scale-105"
        >
          <Sparkles className="w-3.5 h-3.5 text-sand-300 animate-spin" style={{ animationDuration: '6s' }} />
          <span className="hidden xs:inline">Ask Travel AI</span>
        </button>

        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-full hover:bg-cream-200 text-slate-600 hover:text-slate-900 transition-colors relative"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-cream-100"></span>
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-soft-xl border border-sand-200 p-3 z-50 text-xs animate-in fade-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-sand-100 font-semibold text-slate-800">
                <span>Trip Notifications</span>
                <span className="text-[10px] text-forest-700 bg-forest-50 px-2 py-0.5 rounded-full">2 New</span>
              </div>
              <div className="space-y-2">
                {notifications.map((n) => (
                  <div key={n.id} className={`p-2.5 rounded-xl transition-colors ${n.unread ? 'bg-cream-100/80 border border-sand-200/60' : 'hover:bg-cream-50'}`}>
                    <div className="flex items-center justify-between font-medium text-slate-800 mb-0.5">
                      <span>{n.title}</span>
                      <span className="text-[10px] text-slate-400">{n.time}</span>
                    </div>
                    <p className="text-[11px] text-slate-600 leading-relaxed">{n.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User Avatar */}
        <div 
          onClick={() => navigate('/settings')}
          className="flex items-center gap-2 pl-2 cursor-pointer group"
        >
          <img
            src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80"
            alt="Profile"
            className="w-8 h-8 rounded-full object-cover ring-2 ring-forest-700/20 group-hover:ring-forest-700 transition-all"
          />
        </div>
      </div>
    </header>
  );
}

