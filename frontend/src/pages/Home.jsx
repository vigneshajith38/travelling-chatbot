import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, Compass, MapPin, Calendar, Users, 
  Wallet, ArrowRight, Star, Heart, TrendingUp, ShieldCheck
} from 'lucide-react';
import { api } from '../services/api';
import { useTrip } from '../context/TripContext';

const CATEGORIES = [
  { name: 'Mountains', icon: '⛰️', desc: 'Misty heights & serene trails' },
  { name: 'Beaches', icon: '🏖️', desc: 'Golden sands & turquoise waves' },
  { name: 'Romantic getaways', icon: '✨', desc: 'Intimate stays & sunset cruises' },
  { name: 'Cultural experiences', icon: '🏛️', desc: 'Ancient temples & heritage havelis' },
  { name: 'Adventure', icon: '🥾', desc: 'Cliff treks, jeep safaris & rapids' },
  { name: 'Relaxation', icon: '☕', desc: 'Coffee plantations & ayurvedic wellness' },
  { name: 'Food experiences', icon: '🍲', desc: 'Authentic regional culinary trails' },
  { name: 'Budget travel', icon: '🎒', desc: 'Backpacking hostels & hidden vistas' }
];

export default function Home() {
  const navigate = useNavigate();
  const { trips, openChatWithPrompt } = useTrip();

  const [destinations, setDestinations] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  // Quick planner state
  const [origin, setOrigin] = useState('Bengaluru');
  const [destinationInput, setDestinationInput] = useState('');
  const [dates, setDates] = useState('2026-11-20');
  const [travellers, setTravellers] = useState('2');
  const [budgetTier, setBudgetTier] = useState('20000');
  const [preference, setPreference] = useState('mountains');

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const allDest = await api.getDestinations();
        setDestinations(allDest);

        // Personalized recommendations based on preferred styles
        const rec = await api.recommendDestinations({
          interests: ['mountains', 'scenic', 'peaceful'],
          budget_range: 'moderate',
          duration_days: 4,
          travellers_count: 2
        });
        setRecommendations(rec.slice(0, 3));
      } catch (err) {
        console.error('Home load error:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleQuickPlan = (e) => {
    e.preventDefault();
    const dest = destinationInput.trim() || 'Munnar, Kerala';
    navigate(`/planner?destination=${encodeURIComponent(dest)}&origin=${encodeURIComponent(origin)}&travellers=${travellers}&budget=${budgetTier}&date=${dates}`);
  };

  const handleSurpriseMe = async () => {
    try {
      const surprise = await api.getSurpriseMe();
      navigate(`/planner?destination=${encodeURIComponent(surprise.name)}&surprise=true`);
    } catch (err) {
      navigate('/planner?destination=Munnar,%20Kerala');
    }
  };

  return (
    <div className="space-y-12 pb-16">
      {/* 1. Hero Section */}
      <section className="relative rounded-3xl overflow-hidden min-h-[520px] flex items-center shadow-soft-xl border border-forest-900/10">
        <img
          src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=2000&q=85"
          alt="Scenic Mountain Valley"
          className="absolute inset-0 w-full h-full object-cover object-center filter brightness-90"
        />
        {/* Soft elegant gradient scrim overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-forest-950/90 via-forest-900/60 to-transparent" />

        <div className="relative z-10 px-6 sm:px-12 lg:px-16 py-12 max-w-2xl text-white space-y-5">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-sand-400/20 backdrop-blur-md border border-sand-300/40 text-sand-300 font-semibold text-xs tracking-wider uppercase">
            <Sparkles className="w-3.5 h-3.5 text-sand-300 animate-spin" style={{ animationDuration: '6s' }} />
            <span>Next-Gen Travel Intelligence</span>
          </div>

          <h1 className="font-serif text-3xl sm:text-5xl font-extrabold tracking-tight leading-[1.15] text-white">
            Your next adventure <br className="hidden sm:inline" />starts here.
          </h1>

          <p className="text-sm sm:text-base text-cream-200/90 font-light leading-relaxed max-w-lg">
            Discover breathtaking places, plan smarter and travel better with conversational AI tailored to your preferences, mood, and budget.
          </p>

          <div className="flex flex-wrap items-center gap-3.5 pt-2">
            <button
              onClick={() => navigate('/planner')}
              className="px-6 py-3 rounded-full bg-sand-400 hover:bg-sand-300 text-forest-950 font-bold text-xs sm:text-sm tracking-wide shadow-soft-md transition-all hover:scale-105 active:scale-95 flex items-center gap-2"
            >
              <span>Plan My Trip</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate('/explore')}
              className="px-6 py-3 rounded-full bg-forest-900/70 hover:bg-forest-900/90 text-white font-semibold text-xs sm:text-sm backdrop-blur-md border border-white/20 transition-all hover:scale-105"
            >
              Explore Destinations
            </button>
          </div>
        </div>
      </section>

      {/* 2. Quick Trip Planner Bar */}
      <section className="-mt-8 relative z-20 mx-4 sm:mx-8">
        <form
          onSubmit={handleQuickPlan}
          className="p-5 sm:p-6 rounded-3xl bg-white shadow-soft-xl border border-sand-300/80 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3.5 items-end text-xs"
        >
          {/* Starting Location */}
          <div className="space-y-1">
            <label className="font-bold text-slate-700 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-forest-700" />
              <span>Starting From</span>
            </label>
            <input
              type="text"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              placeholder="e.g. Mumbai, Delhi"
              className="w-full px-3 py-2 rounded-xl bg-cream-50 border border-sand-300 text-slate-800 focus:bg-white focus:ring-1 focus:ring-forest-600"
            />
          </div>

          {/* Destination */}
          <div className="space-y-1">
            <div className="flex justify-between items-center">
              <label className="font-bold text-slate-700 flex items-center gap-1.5">
                <Compass className="w-3.5 h-3.5 text-forest-700" />
                <span>Destination</span>
              </label>
              <button
                type="button"
                onClick={handleSurpriseMe}
                className="text-[10px] text-forest-700 hover:text-forest-900 font-bold underline"
              >
                Surprise Me
              </button>
            </div>
            <input
              type="text"
              value={destinationInput}
              onChange={(e) => setDestinationInput(e.target.value)}
              placeholder="Where to? (or leave blank)"
              className="w-full px-3 py-2 rounded-xl bg-cream-50 border border-sand-300 text-slate-800 focus:bg-white focus:ring-1 focus:ring-forest-600"
            />
          </div>

          {/* Dates */}
          <div className="space-y-1">
            <label className="font-bold text-slate-700 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-forest-700" />
              <span>Travel Date</span>
            </label>
            <input
              type="date"
              value={dates}
              onChange={(e) => setDates(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-cream-50 border border-sand-300 text-slate-800 focus:bg-white"
            />
          </div>

          {/* Travellers */}
          <div className="space-y-1">
            <label className="font-bold text-slate-700 flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-forest-700" />
              <span>Travellers</span>
            </label>
            <select
              value={travellers}
              onChange={(e) => setTravellers(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-cream-50 border border-sand-300 text-slate-800"
            >
              <option value="1">Solo Explorer (1)</option>
              <option value="2">Couple / Duo (2)</option>
              <option value="3">Friends Group (3)</option>
              <option value="4">Small Group (4)</option>
              <option value="6">Family (6)</option>
            </select>
          </div>

          {/* Budget */}
          <div className="space-y-1">
            <label className="font-bold text-slate-700 flex items-center gap-1.5">
              <Wallet className="w-3.5 h-3.5 text-forest-700" />
              <span>Budget (₹)</span>
            </label>
            <select
              value={budgetTier}
              onChange={(e) => setBudgetTier(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-cream-50 border border-sand-300 text-slate-800"
            >
              <option value="12000">₹12,000 (Budget)</option>
              <option value="20000">₹20,000 (Moderate)</option>
              <option value="35000">₹35,000 (Comfort)</option>
              <option value="60000">₹60,000+ (Luxury)</option>
            </select>
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="w-full py-2.5 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-soft-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-sand-300" />
            <span>Generate Plan</span>
          </button>
        </form>
      </section>

      {/* 3. Travel Inspiration Categories */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-serif font-bold text-xl sm:text-2xl text-slate-900">
              Travel Inspiration & Moods
            </h2>
            <p className="text-xs text-slate-500">Pick a vibe and let WanderWise match offbeat destinations.</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          {CATEGORIES.map((cat) => (
            <div
              key={cat.name}
              onClick={() => navigate(`/explore?category=${encodeURIComponent(cat.name)}`)}
              className="cursor-pointer p-3.5 rounded-2xl bg-white hover:bg-forest-50 border border-sand-200 hover:border-forest-600 transition-all text-center group shadow-soft-sm hover:-translate-y-1"
            >
              <span className="text-2xl mb-1.5 block group-hover:scale-110 transition-transform">
                {cat.icon}
              </span>
              <span className="font-semibold text-xs text-slate-800 group-hover:text-forest-800 block truncate">
                {cat.name}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* 4. Upcoming Saved Trips */}
      {trips.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-serif font-bold text-xl sm:text-2xl text-slate-900">
                Your Upcoming Journeys
              </h2>
              <p className="text-xs text-slate-500">Pick up right where you left off in planning.</p>
            </div>
            <button
              onClick={() => navigate('/my-trips')}
              className="text-xs font-bold text-forest-800 hover:text-forest-900 flex items-center gap-1"
            >
              <span>View All ({trips.length})</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {trips.slice(0, 3).map((trip) => (
              <div
                key={trip.id}
                onClick={() => navigate(`/trips/${trip.id}`)}
                className="group cursor-pointer rounded-2xl bg-white border border-sand-200 overflow-hidden shadow-soft-sm hover:shadow-soft-md transition-all hover:-translate-y-1"
              >
                <div className="relative h-44 overflow-hidden">
                  <img
                    src={trip.cover_image || 'https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=800&q=80'}
                    alt={trip.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-3 left-3 px-2.5 py-1 rounded-full bg-forest-900/80 backdrop-blur-md text-sand-300 font-bold text-[10px] uppercase tracking-wider">
                    {trip.status}
                  </div>
                </div>

                <div className="p-4 space-y-2">
                  <h3 className="font-serif font-bold text-base text-slate-900 group-hover:text-forest-800 transition-colors">
                    {trip.title}
                  </h3>
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-forest-700" />
                      {trip.destination}
                    </span>
                    <span className="font-semibold text-slate-800">
                      ₹{trip.total_budget?.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 5. Recommended For You */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-serif font-bold text-xl sm:text-2xl text-slate-900">
                Recommended For You
              </h2>
              <span className="px-2 py-0.5 rounded-full bg-forest-100 text-forest-800 font-bold text-[10px]">
                AI Match
              </span>
            </div>
            <p className="text-xs text-slate-500">Personalized destinations based on your travel interests.</p>
          </div>
          <button
            onClick={() => navigate('/explore')}
            className="text-xs font-bold text-forest-800 hover:text-forest-900 flex items-center gap-1"
          >
            <span>See More</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {recommendations.map((dest) => (
            <div
              key={dest.id}
              onClick={() => navigate(`/planner?destination=${encodeURIComponent(dest.name)}`)}
              className="group cursor-pointer rounded-2xl bg-white border border-sand-200 overflow-hidden shadow-soft-sm hover:shadow-soft-md transition-all hover:-translate-y-1 flex flex-col justify-between"
            >
              <div>
                <div className="relative h-48 overflow-hidden">
                  <img
                    src={dest.image_url}
                    alt={dest.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-3 right-3 px-2 py-0.5 rounded-md bg-white/90 backdrop-blur-md text-slate-800 font-bold text-xs flex items-center gap-1">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    <span>{dest.rating}</span>
                  </div>
                  <div className="absolute bottom-3 left-3 px-2.5 py-1 rounded-full bg-forest-900/80 backdrop-blur-md text-sand-300 font-bold text-[10px]">
                    {dest.match_score}% Preference Match
                  </div>
                </div>

                <div className="p-4 space-y-1.5">
                  <h3 className="font-serif font-bold text-base text-slate-900 group-hover:text-forest-800 transition-colors">
                    {dest.name}
                  </h3>
                  <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">{dest.description}</p>
                </div>
              </div>

              <div className="px-4 pb-4 pt-2 border-t border-sand-100 flex items-center justify-between text-xs">
                <div>
                  <span className="text-[11px] text-slate-400 block">Est. Daily Budget</span>
                  <span className="font-bold text-forest-900">₹{dest.estimated_daily_budget?.toLocaleString()}</span>
                </div>
                <button className="px-3 py-1.5 rounded-xl bg-forest-50 text-forest-800 group-hover:bg-forest-800 group-hover:text-white font-semibold transition-colors">
                  Plan Trip
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 6. Popular Destinations Grid */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-serif font-bold text-xl sm:text-2xl text-slate-900">
              Popular Destinations
            </h2>
            <p className="text-xs text-slate-500">Trending landscapes, heritage corridors, and coastal escapes.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {destinations.slice(0, 8).map((dest) => (
            <div
              key={dest.id}
              onClick={() => navigate(`/planner?destination=${encodeURIComponent(dest.name)}`)}
              className="group cursor-pointer rounded-2xl bg-white border border-sand-200 overflow-hidden shadow-soft-sm hover:shadow-soft-md transition-all hover:-translate-y-1 flex flex-col justify-between"
            >
              <div>
                <div className="relative h-40 overflow-hidden">
                  <img
                    src={dest.image_url}
                    alt={dest.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-2.5 right-2.5 px-2 py-0.5 rounded-md bg-white/90 backdrop-blur-md text-slate-800 font-bold text-[11px] flex items-center gap-1">
                    <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                    <span>{dest.rating}</span>
                  </div>
                </div>

                <div className="p-3.5 space-y-1">
                  <h4 className="font-serif font-bold text-sm text-slate-900 group-hover:text-forest-800 transition-colors truncate">
                    {dest.name}
                  </h4>
                  <p className="text-[11px] text-slate-500 font-medium">Best: {dest.best_season}</p>
                </div>
              </div>

              <div className="px-3.5 pb-3.5 pt-1.5 border-t border-sand-100 flex items-center justify-between text-[11px]">
                <span className="font-semibold text-slate-700">₹{dest.estimated_daily_budget}/day</span>
                <span className="text-forest-700 font-bold group-hover:underline">Explore →</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
