import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, UserPlus, ArrowRight, Sparkles, Key, 
  MapPin, Calendar, Wallet, Check
} from 'lucide-react';
import { useTrip } from '../context/TripContext';
import { api } from '../services/api';

export default function GroupTrips() {
  const navigate = useNavigate();
  const { trips, refreshTrips } = useTrip();
  const [joinCode, setJoinCode] = useState('');
  const [joining, setJoining] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const groupTrips = trips.filter(t => t.is_group);

  const handleJoin = async (e) => {
    e.preventDefault();
    if (!joinCode.trim()) return;
    setJoining(true);
    setErrorMsg('');
    try {
      const res = await api.joinTripByCode(joinCode.trim());
      await refreshTrips();
      navigate(`/trips/${res.trip_id}?tab=group`);
    } catch (err) {
      setErrorMsg('Invalid invite code. Please check with your trip organizer.');
    } finally {
      setJoining(false);
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Banner */}
      <div className="p-8 rounded-3xl bg-forest-900 text-cream-100 shadow-soft-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-forest-800 border border-sand-400/40 text-sand-300 font-semibold text-xs">
            <Users className="w-3.5 h-3.5" />
            <span>Group Travel Hub</span>
          </div>
          <h1 className="font-serif font-bold text-2xl sm:text-3xl text-white">
            Plan, Vote & Travel Together
          </h1>
          <p className="text-xs sm:text-sm text-cream-200/80 leading-relaxed font-light">
            Share itineraries with friends, vote on candidate spots, and automatically resolve group expense splitting without awkward math.
          </p>
        </div>

        {/* Join Trip Code Box */}
        <form onSubmit={handleJoin} className="p-4 rounded-2xl bg-forest-800/90 border border-forest-700/80 space-y-2 shrink-0 w-full md:w-80 shadow-soft-md">
          <label className="block text-xs font-semibold text-sand-300">Have an Invite Code?</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
              placeholder="e.g. MUNNAR26"
              className="flex-1 px-3 py-2 rounded-xl bg-forest-950/80 border border-forest-700 text-xs text-white uppercase tracking-wider font-mono focus:outline-none focus:ring-1 focus:ring-sand-400"
              required
            />
            <button
              type="submit"
              disabled={joining}
              className="px-4 py-2 rounded-xl bg-sand-400 hover:bg-sand-300 text-forest-950 font-bold text-xs shrink-0 transition-colors"
            >
              {joining ? 'Joining...' : 'Join'}
            </button>
          </div>
          {errorMsg && <p className="text-[11px] text-rose-300">{errorMsg}</p>}
        </form>
      </div>

      {/* Active Group Trips */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-serif font-bold text-lg text-slate-900">
            Active Group Trips ({groupTrips.length})
          </h3>
          <button
            onClick={() => navigate('/planner')}
            className="text-xs font-bold text-forest-800 hover:text-forest-900 flex items-center gap-1"
          >
            <span>Start a Group Trip</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {groupTrips.length === 0 ? (
          <div className="p-12 rounded-3xl bg-white border border-sand-200 text-center space-y-3">
            <Users className="w-10 h-10 text-sand-400 mx-auto" />
            <h4 className="font-serif font-bold text-base text-slate-800">No group trips yet</h4>
            <p className="text-xs text-slate-500">Create a trip and enable "Group Collaboration Mode" to invite friends.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groupTrips.map((trip) => (
              <div
                key={trip.id}
                onClick={() => navigate(`/trips/${trip.id}?tab=group`)}
                className="group cursor-pointer rounded-2xl bg-white border border-sand-200 overflow-hidden shadow-soft-sm hover:shadow-soft-md transition-all hover:-translate-y-1 p-5 space-y-4 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-800 font-bold text-[10px] uppercase">
                      Code: {trip.share_code || 'ACTIVE'}
                    </span>
                    <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
                      <Users className="w-3.5 h-3.5 text-forest-700" />
                      {trip.travellers_count} Members
                    </span>
                  </div>

                  <h4 className="font-serif font-bold text-base text-slate-900 group-hover:text-forest-800 transition-colors">
                    {trip.title}
                  </h4>
                  <p className="text-xs text-slate-600 flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{trip.destination}</span>
                  </p>
                </div>

                <div className="pt-3 border-t border-sand-100 flex items-center justify-between text-xs">
                  <span className="font-bold text-forest-800">₹{trip.total_budget?.toLocaleString()}</span>
                  <span className="text-forest-700 font-semibold flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                    Open Group Hub <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
