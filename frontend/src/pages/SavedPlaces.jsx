import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bookmark, MapPin, Star, Trash2, Plus, 
  ArrowRight, Sparkles, Navigation
} from 'lucide-react';
import { api } from '../services/api';

export default function SavedPlaces() {
  const navigate = useNavigate();
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlaces();
  }, []);

  const fetchPlaces = async () => {
    setLoading(true);
    try {
      const data = await api.getSavedPlaces();
      setPlaces(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteSavedPlace(id);
      setPlaces(prev => prev.filter(p => p.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-forest-700 font-semibold text-xs mb-1">
            <Bookmark className="w-4 h-4" />
            <span>Wishlist & Bucket List</span>
          </div>
          <h1 className="font-serif font-bold text-2xl sm:text-3xl text-slate-900">
            Saved Places & Sights ({places.length})
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Bookmarked viewpoints, cafes, and heritage spots ready to be incorporated into your next trip.
          </p>
        </div>

        <button
          onClick={() => navigate('/explore')}
          className="px-5 py-2.5 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-bold text-xs flex items-center gap-2 shadow-soft-sm transition-all shrink-0"
        >
          <Sparkles className="w-4 h-4 text-sand-300" />
          <span>Discover More Places</span>
        </button>
      </div>

      {/* Places Grid */}
      {places.length === 0 ? (
        <div className="p-12 rounded-3xl bg-white border border-sand-200 text-center space-y-3">
          <Bookmark className="w-10 h-10 text-sand-400 mx-auto" />
          <h3 className="font-serif font-bold text-base text-slate-800">Your bucket list is empty</h3>
          <p className="text-xs text-slate-500">Tap the bookmark icon on any destination in Explore to save it here.</p>
          <button
            onClick={() => navigate('/explore')}
            className="px-4 py-2 rounded-xl bg-forest-800 text-white text-xs font-semibold"
          >
            Explore Destinations
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {places.map((place) => (
            <div
              key={place.id}
              className="group rounded-2xl bg-white border border-sand-200 overflow-hidden shadow-soft-sm hover:shadow-soft-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="relative h-44 overflow-hidden">
                  <img
                    src={place.image_url || 'https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=800&q=80'}
                    alt={place.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-3 right-3 px-2 py-0.5 rounded-md bg-white/90 backdrop-blur-md text-slate-800 font-bold text-xs flex items-center gap-1 shadow-sm">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    <span>{place.rating}</span>
                  </div>
                  <button
                    onClick={() => handleDelete(place.id)}
                    className="absolute top-3 left-3 p-1.5 rounded-full bg-slate-900/60 hover:bg-rose-600 text-white backdrop-blur-md transition-colors"
                    title="Remove from Bucket List"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="p-4 space-y-2">
                  <h3 className="font-serif font-bold text-base text-slate-900 group-hover:text-forest-800 transition-colors">
                    {place.name}
                  </h3>
                  <p className="text-xs text-slate-500 flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-forest-700" />
                    <span>{place.destination}</span>
                  </p>
                  {place.description && (
                    <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                      {place.description}
                    </p>
                  )}
                  {place.notes && (
                    <div className="p-2.5 rounded-lg bg-sand-100/60 border border-sand-200 text-[11px] text-slate-700">
                      <span className="font-semibold text-forest-800">Note: </span>
                      {place.notes}
                    </div>
                  )}
                </div>
              </div>

              <div className="p-4 border-t border-sand-100 flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700">Est. ₹{place.estimated_cost}</span>
                <button
                  onClick={() => navigate(`/planner?destination=${encodeURIComponent(place.destination)}`)}
                  className="px-3.5 py-1.5 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-semibold text-xs flex items-center gap-1 transition-colors"
                >
                  <span>Plan Itinerary</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
