import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Compass, Sparkles, Star, MapPin, Heart, Bookmark, 
  Search, SlidersHorizontal, ArrowRight, Eye, Smile
} from 'lucide-react';
import { api } from '../services/api';

export default function Explore() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialCat = queryParams.get('category') || 'All';
  const initialSearch = queryParams.get('search') || '';

  const [destinations, setDestinations] = useState([]);
  const [hiddenGems, setHiddenGems] = useState([]);
  const [activeTab, setActiveTab] = useState('all'); // all, mood, gems
  const [category, setCategory] = useState(initialCat);
  const [searchTerm, setSearchTerm] = useState(initialSearch);
  const [loading, setLoading] = useState(true);

  // Mood Planner State
  const [moodInput, setMoodInput] = useState('');
  const [moodResult, setMoodResult] = useState(null);
  const [moodLoading, setMoodLoading] = useState(false);

  // Surprise modal
  const [surpriseDest, setSurpriseDest] = useState(null);

  const categories = ['All', 'Mountains', 'Beaches', 'Romantic getaways', 'Cultural experiences', 'Adventure', 'Relaxation', 'Food experiences', 'Budget travel'];

  useEffect(() => {
    fetchDestinations();
  }, [category, searchTerm]);

  const fetchDestinations = async () => {
    setLoading(true);
    try {
      const data = await api.getDestinations({
        category: category !== 'All' ? category : undefined,
        search: searchTerm || undefined
      });
      setDestinations(data);

      const gems = await api.getHiddenGems();
      setHiddenGems(gems);
    } catch (err) {
      console.error('Explore error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSurpriseMe = async () => {
    try {
      const res = await api.getSurpriseMe();
      setSurpriseDest(res);
    } catch (err) {
      console.error(err);
    }
  };

  const handleMoodSubmit = async (e) => {
    e.preventDefault();
    if (!moodInput.trim()) return;
    setMoodLoading(true);
    try {
      const res = await api.getMoodPlan({
        mood_description: moodInput.trim(),
        duration_days: 4
      });
      setMoodResult(res);
    } catch (err) {
      console.error('Mood error:', err);
    } finally {
      setMoodLoading(false);
    }
  };

  const handleSavePlace = async (dest, e) => {
    e.stopPropagation();
    try {
      await api.savePlace({
        name: dest.name,
        destination: dest.name,
        category: dest.category,
        rating: dest.rating,
        image_url: dest.image_url,
        description: dest.description,
        lat: dest.lat,
        lng: dest.lng,
        estimated_cost: dest.estimated_daily_budget,
        notes: `Best visiting season: ${dest.best_season}`
      });
      alert(`Saved "${dest.name}" to your Bucket List!`);
    } catch (err) {
      alert('Place is already in your bucket list.');
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Header Banner */}
      <div className="p-8 rounded-3xl bg-forest-900 text-cream-100 shadow-soft-xl flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="space-y-2 z-10 max-w-xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-forest-800 border border-sand-400/40 text-sand-300 font-semibold text-xs">
            <Compass className="w-3.5 h-3.5 animate-spin" style={{ animationDuration: '10s' }} />
            <span>Destination Discovery Hub</span>
          </div>
          <h1 className="font-serif font-bold text-2xl sm:text-3xl text-white">
            Explore Handpicked Destinations
          </h1>
          <p className="text-xs sm:text-sm text-cream-200/80 leading-relaxed font-light">
            Filter by geographic landscapes, browse verified offbeat hidden gems, or let WanderWise match your current mood.
          </p>
        </div>

        <button
          onClick={handleSurpriseMe}
          className="z-10 px-5 py-3 rounded-2xl bg-sand-400 hover:bg-sand-300 text-forest-950 font-bold text-xs shrink-0 flex items-center justify-center gap-2 shadow-soft-md transition-all hover:scale-105"
        >
          <Sparkles className="w-4 h-4" />
          <span>Surprise Me!</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-sand-200 text-xs font-semibold gap-6">
        <button
          onClick={() => setActiveTab('all')}
          className={`pb-3 transition-colors border-b-2 flex items-center gap-1.5 ${
            activeTab === 'all'
              ? 'border-forest-800 text-forest-900 font-bold'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Compass className="w-4 h-4" />
          <span>All Destinations ({destinations.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('mood')}
          className={`pb-3 transition-colors border-b-2 flex items-center gap-1.5 ${
            activeTab === 'mood'
              ? 'border-forest-800 text-forest-900 font-bold'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Smile className="w-4 h-4 text-sand-500" />
          <span>Mood-Based Travel Planner</span>
        </button>

        <button
          onClick={() => setActiveTab('gems')}
          className={`pb-3 transition-colors border-b-2 flex items-center gap-1.5 ${
            activeTab === 'gems'
              ? 'border-forest-800 text-forest-900 font-bold'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Sparkles className="w-4 h-4 text-amber-500" />
          <span>Verified Hidden Gems ({hiddenGems.length})</span>
        </button>
      </div>

      {/* TAB 1: ALL DESTINATIONS */}
      {activeTab === 'all' && (
        <div className="space-y-6">
          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex flex-wrap gap-1.5 overflow-x-auto w-full sm:w-auto">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setCategory(cat)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                    category === cat
                      ? 'bg-forest-800 text-white shadow-soft-sm'
                      : 'bg-white hover:bg-cream-200 text-slate-700 border border-sand-300'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            <div className="relative w-full sm:w-64">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search places..."
                className="w-full pl-8 pr-3 py-1.5 rounded-full bg-white border border-sand-300 text-xs focus:ring-1 focus:ring-forest-600"
              />
            </div>
          </div>

          {/* Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {destinations.map((dest) => (
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
                    <div className="absolute top-3 right-3 px-2 py-0.5 rounded-md bg-white/90 backdrop-blur-md text-slate-800 font-bold text-xs flex items-center gap-1 shadow-sm">
                      <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                      <span>{dest.rating}</span>
                    </div>
                    <button
                      onClick={(e) => handleSavePlace(dest, e)}
                      className="absolute top-3 left-3 p-2 rounded-full bg-forest-900/70 hover:bg-forest-900 text-white backdrop-blur-md transition-all shadow-sm"
                      title="Save to Bucket List"
                    >
                      <Bookmark className="w-3.5 h-3.5" />
                    </button>
                    {dest.is_hidden_gem && (
                      <div className="absolute bottom-3 left-3 px-2.5 py-0.5 rounded-full bg-amber-500 text-forest-950 font-extrabold text-[10px] tracking-wide uppercase">
                        Hidden Gem
                      </div>
                    )}
                  </div>

                  <div className="p-4 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <h3 className="font-serif font-bold text-base text-slate-900 group-hover:text-forest-800 transition-colors">
                        {dest.name}
                      </h3>
                      <span className="text-[10px] font-semibold text-slate-500 uppercase">
                        {dest.category}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                      {dest.description}
                    </p>
                    <div className="flex flex-wrap gap-1 pt-1">
                      {dest.highlights?.slice(0, 2).map((h, i) => (
                        <span key={i} className="text-[10px] font-medium bg-sand-100/70 text-slate-700 px-2 py-0.5 rounded-md">
                          {h}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="px-4 pb-4 pt-2 border-t border-sand-100 flex items-center justify-between text-xs">
                  <div>
                    <span className="text-[11px] text-slate-400 block">Est. Daily Budget</span>
                    <span className="font-bold text-forest-900">₹{dest.estimated_daily_budget?.toLocaleString()}</span>
                  </div>
                  <span className="text-forest-700 font-bold text-xs flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                    Plan Trip <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: MOOD-BASED TRAVEL PLANNER */}
      {activeTab === 'mood' && (
        <div className="space-y-6">
          <div className="p-6 rounded-3xl bg-white border border-sand-200 shadow-soft-sm space-y-4">
            <div>
              <h3 className="font-serif font-bold text-lg text-slate-900">
                How do you want to feel on this journey?
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Describe your desired emotional state or travel mood rather than a specific city name.
              </p>
            </div>

            <form onSubmit={handleMoodSubmit} className="space-y-3">
              <textarea
                value={moodInput}
                onChange={(e) => setMoodInput(e.target.value)}
                placeholder="e.g. 'I want to disconnect from everything, breathe crisp mountain air, drink artisan coffee, and watch sunsets from quiet cliffs'..."
                rows="3"
                className="w-full p-4 rounded-2xl bg-cream-50 border border-sand-300 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-forest-600 focus:bg-white transition-all"
                required
              />

              <div className="flex flex-wrap gap-2 text-xs">
                {[
                  "I want to disconnect from everything.",
                  "I want a romantic weekend getaway.",
                  "I want an adventurous road trip with mountain trails.",
                  "I want a quiet photography-focused trip."
                ].map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setMoodInput(preset)}
                    className="px-3 py-1 rounded-full bg-cream-100 hover:bg-cream-200 border border-sand-300 text-[11px] text-slate-700 transition-colors"
                  >
                    "{preset}"
                  </button>
                ))}
              </div>

              <button
                type="submit"
                disabled={moodLoading}
                className="px-6 py-2.5 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-bold text-xs flex items-center gap-2 shadow-soft-sm transition-all"
              >
                <Sparkles className="w-4 h-4 text-sand-300" />
                <span>{moodLoading ? 'Analyzing Mood...' : 'Translate Mood Into Itinerary'}</span>
              </button>
            </form>
          </div>

          {/* Mood Analysis Output */}
          {moodResult && (
            <div className="p-6 rounded-3xl bg-forest-900 text-cream-100 space-y-5 shadow-soft-xl border border-forest-800">
              <div className="flex items-center justify-between border-b border-forest-800 pb-3">
                <div>
                  <span className="text-[10px] uppercase font-bold text-sand-300 tracking-wider">
                    Recommended Mood Match
                  </span>
                  <h4 className="font-serif font-bold text-lg text-white">
                    {moodResult.top_destination?.name}
                  </h4>
                </div>
                <button
                  onClick={() => navigate(`/planner?destination=${encodeURIComponent(moodResult.top_destination?.name)}`)}
                  className="px-4 py-2 rounded-xl bg-sand-400 hover:bg-sand-300 text-forest-950 font-bold text-xs flex items-center gap-1.5 transition-colors"
                >
                  <span>Build Full Itinerary</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                {moodResult.curated_insights?.map((insight, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-forest-800/80 border border-forest-700/60 text-cream-200">
                    {insight}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: HIDDEN GEMS */}
      {activeTab === 'gems' && (
        <div className="space-y-6">
          <div className="p-6 rounded-3xl bg-cream-50 border border-sand-200 space-y-1">
            <h3 className="font-serif font-bold text-lg text-slate-900">
              Verified Lesser-Known Havens
            </h3>
            <p className="text-xs text-slate-500">
              Authentic cultural hamlets, uncommercialized mountain valleys, and untouched coastal cliff trails.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {hiddenGems.map((gem) => (
              <div
                key={gem.id}
                onClick={() => navigate(`/planner?destination=${encodeURIComponent(gem.name)}`)}
                className="group cursor-pointer rounded-2xl bg-white border border-sand-200 overflow-hidden shadow-soft-sm hover:shadow-soft-md transition-all hover:-translate-y-1 flex flex-col sm:flex-row"
              >
                <div className="sm:w-48 h-48 sm:h-auto relative shrink-0 overflow-hidden">
                  <img
                    src={gem.image_url}
                    alt={gem.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-2.5 left-2.5 px-2 py-0.5 rounded-full bg-amber-500 text-forest-950 font-extrabold text-[10px] uppercase">
                    Offbeat
                  </div>
                </div>

                <div className="p-5 flex-1 flex flex-col justify-between space-y-3">
                  <div>
                    <div className="flex items-center justify-between">
                      <h4 className="font-serif font-bold text-base text-slate-900 group-hover:text-forest-800">
                        {gem.name}
                      </h4>
                      <span className="text-xs font-bold text-amber-500 flex items-center gap-1">
                        <Star className="w-3.5 h-3.5 fill-amber-400" />
                        {gem.rating}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 line-clamp-2 mt-1 leading-relaxed">
                      {gem.description}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-sand-100 flex items-center justify-between text-xs">
                    <span className="font-semibold text-forest-800">₹{gem.estimated_daily_budget}/day</span>
                    <span className="font-bold text-forest-700 flex items-center gap-1">
                      Explore Gem →
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Surprise Me Modal */}
      {surpriseDest && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full overflow-hidden shadow-2xl border border-sand-300 animate-in zoom-in-95 duration-200">
            <div className="relative h-56">
              <img
                src={surpriseDest.image_url}
                alt={surpriseDest.name}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-forest-950/80 to-transparent flex items-end p-5 text-white">
                <div>
                  <span className="text-[10px] uppercase font-bold tracking-wider text-sand-300">
                    Surprise AI Pick
                  </span>
                  <h3 className="font-serif font-bold text-xl">{surpriseDest.name}</h3>
                </div>
              </div>
            </div>

            <div className="p-6 space-y-4 text-xs">
              <p className="text-slate-600 leading-relaxed">{surpriseDest.description}</p>
              <div className="p-3 rounded-xl bg-forest-50 border border-forest-200 text-forest-900 font-medium">
                {surpriseDest.why_selected}
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  onClick={() => setSurpriseDest(null)}
                  className="px-4 py-2 rounded-xl text-slate-600 hover:bg-cream-200 font-semibold"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    navigate(`/planner?destination=${encodeURIComponent(surpriseDest.name)}`);
                    setSurpriseDest(null);
                  }}
                  className="px-5 py-2 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-bold flex items-center gap-1.5"
                >
                  <span>Plan This Adventure</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
