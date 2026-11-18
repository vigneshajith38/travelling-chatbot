import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, Compass, Sparkles, Luggage, Users, 
  Wallet, Bookmark, Settings, MessageSquare
} from 'lucide-react';
import { useTrip } from '../../context/TripContext';

const NAV_ITEMS = [
  { name: 'Home', path: '/', icon: Home },
  { name: 'AI Trip Planner', path: '/planner', icon: Sparkles, badge: 'AI' },
  { name: 'Explore Destinations', path: '/explore', icon: Compass },
  { name: 'My Trips', path: '/my-trips', icon: Luggage },
  { name: 'Group Trips', path: '/group-trips', icon: Users },
  { name: 'Budget Tracker', path: '/budget', icon: Wallet },
  { name: 'Saved Places', path: '/saved-places', icon: Bookmark },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export default function Sidebar() {
  const { openChatWithPrompt } = useTrip();

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex flex-col w-64 bg-forest-900 text-cream-100 border-r border-forest-800 shrink-0 select-none min-h-screen fixed left-0 top-0 bottom-0 z-30">
        {/* Brand Header */}
        <div className="p-6 border-b border-forest-800/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-forest-600 to-skycoast-400 flex items-center justify-center shadow-md">
              <Compass className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <span className="font-serif text-xl font-bold tracking-tight text-white block leading-tight">
                WanderWise
              </span>
              <span className="text-[10px] tracking-widest uppercase font-semibold text-sand-300">
                Smart Travel AI
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 group ${
                    isActive
                      ? 'bg-forest-800 text-white shadow-soft-sm font-semibold border-l-4 border-sand-400'
                      : 'text-cream-300/80 hover:bg-forest-800/50 hover:text-white'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-5 h-5 transition-transform group-hover:scale-110 text-sand-300" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-forest-700 text-sand-300 border border-forest-600">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* AI Quick Assistant Callout */}
        <div className="p-4 mx-3 mb-4 rounded-2xl bg-gradient-to-br from-forest-800 to-forest-950 border border-forest-700/60 shadow-soft-md">
          <div className="flex items-center gap-2 mb-2 text-sand-300 font-semibold text-xs">
            <MessageSquare className="w-4 h-4 text-skycoast-300" />
            <span>AI Travel Assistant</span>
          </div>
          <p className="text-xs text-cream-300/70 mb-3 leading-relaxed">
            Need instant recommendations or itinerary modifications?
          </p>
          <button
            onClick={() => openChatWithPrompt()}
            className="w-full py-2 px-3 rounded-xl bg-forest-700 hover:bg-forest-600 text-white font-medium text-xs flex items-center justify-center gap-1.5 transition-colors shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-sand-300" />
            Ask Assistant
          </button>
        </div>

        {/* User Status pill */}
        <div className="p-4 border-t border-forest-800/80 flex items-center gap-3">
          <img
            src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80"
            alt="Profile"
            className="w-9 h-9 rounded-full object-cover border border-sand-400/50"
          />
          <div className="overflow-hidden">
            <p className="text-xs font-semibold text-white truncate">Aarav Sharma</p>
            <p className="text-[11px] text-cream-400/70 truncate">Solo Explorer & Explorer</p>
          </div>
        </div>
      </aside>

      {/* Mobile Bottom Navigation */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-forest-900 border-t border-forest-800 text-cream-200 z-40 px-2 py-1.5 flex items-center justify-around shadow-2xl">
        {NAV_ITEMS.slice(0, 5).map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex flex-col items-center py-1 px-2 rounded-lg text-[10px] font-medium transition-colors ${
                  isActive ? 'text-sand-300 font-bold' : 'text-cream-300/70 hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5 mb-0.5" />
              <span>{item.name.split(' ')[0]}</span>
            </NavLink>
          );
        })}
      </nav>
    </>
  );
}
