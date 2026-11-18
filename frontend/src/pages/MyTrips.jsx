import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Luggage, Plus, Calendar, Users, Wallet, 
  MapPin, Copy, Trash2, ArrowRight, Share2, Archive, CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';
import { useTrip } from '../context/TripContext';

export default function MyTrips() {
  const navigate = useNavigate();
  const { trips, refreshTrips } = useTrip();
  const [filterStatus, setFilterStatus] = useState('all');

  const filteredTrips = filterStatus === 'all'
    ? trips
    : trips.filter(t => t.status === filterStatus);

  const handleDuplicate = async (tripId, e) => {
    e.stopPropagation();
    try {
      await api.duplicateTrip(tripId);
      await refreshTrips();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (tripId, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this trip?')) return;
    try {
      await api.deleteTrip(tripId);
      await refreshTrips();
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleArchive = async (trip, e) => {
    e.stopPropagation();
    const newStatus = trip.status === 'archived' ? 'planning' : 'archived';
    try {
      await api.updateTrip(trip.id, { status: newStatus });
      await refreshTrips();
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
            <Luggage className="w-4 h-4" />
            <span>Trip Management Dashboard</span>
          </div>
          <h1 className="font-serif font-bold text-2xl sm:text-3xl text-slate-900">
            My Journeys & Expeditions
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage your active itineraries, review completed trips, and collaborate with travel buddies.
          </p>
        </div>

        <button
          onClick={() => navigate('/planner')}
          className="px-5 py-2.5 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-bold text-xs flex items-center gap-2 shadow-soft-sm transition-all shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Plan New Trip</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-sand-200 text-xs font-semibold gap-2">
        {['all', 'planning', 'confirmed', 'completed', 'archived'].map((status) => (
          <button
            key={status}
            onClick={() => setFilterStatus(status)}
            className={`pb-2.5 px-3 uppercase tracking-wider text-[11px] border-b-2 transition-all ${
              filterStatus === status
                ? 'border-forest-800 text-forest-900 font-bold'
                : 'border-transparent text-slate-400 hover:text-slate-700'
            }`}
          >
            {status} ({status === 'all' ? trips.length : trips.filter(t => t.status === status).length})
          </button>
        ))}
      </div>

      {/* Trip Cards Grid */}
      {filteredTrips.length === 0 ? (
        <div className="p-12 rounded-3xl bg-white border border-sand-200 text-center space-y-3">
          <Luggage className="w-12 h-12 text-sand-400 mx-auto" />
          <h3 className="font-serif font-bold text-base text-slate-800">No trips found in this category</h3>
          <p className="text-xs text-slate-500">Ready for your next getaway? Launch the AI Trip Planner.</p>
          <button
            onClick={() => navigate('/planner')}
            className="px-5 py-2.5 rounded-xl bg-forest-800 text-white font-semibold text-xs"
          >
            Plan a Trip
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTrips.map((trip) => (
            <div
              key={trip.id}
              onClick={() => navigate(`/trips/${trip.id}`)}
              className="group cursor-pointer rounded-2xl bg-white border border-sand-200 overflow-hidden shadow-soft-sm hover:shadow-soft-md transition-all hover:-translate-y-1 flex flex-col justify-between"
            >
              <div>
                <div className="relative h-48 overflow-hidden">
                  <img
                    src={trip.cover_image || 'https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=800&q=80'}
                    alt={trip.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-3 left-3 px-2.5 py-1 rounded-full bg-forest-900/80 backdrop-blur-md text-sand-300 font-bold text-[10px] uppercase tracking-wider">
                    {trip.status}
                  </div>
                  {trip.is_group && (
                    <div className="absolute top-3 right-3 px-2 py-0.5 rounded-md bg-white/90 text-forest-900 font-bold text-[10px]">
                      Group
                    </div>
                  )}
                </div>

                <div className="p-5 space-y-2">
                  <h3 className="font-serif font-bold text-base text-slate-900 group-hover:text-forest-800 transition-colors">
                    {trip.title}
                  </h3>
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span className="flex items-center gap-1 font-medium text-slate-700">
                      <MapPin className="w-3.5 h-3.5 text-forest-700" />
                      {trip.destination}
                    </span>
                    <span className="font-bold text-forest-800">
                      ₹{trip.total_budget?.toLocaleString()}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-[11px] text-slate-500 pt-1">
                    <Calendar className="w-3.5 h-3.5 text-sand-500" />
                    <span>{trip.start_date} → {trip.end_date}</span>
                  </div>
                </div>
              </div>

              {/* Card Actions */}
              <div className="px-5 pb-4 pt-2 border-t border-sand-100 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => handleDuplicate(trip.id, e)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-cream-200 transition-colors"
                    title="Duplicate Trip"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => handleToggleArchive(trip, e)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-cream-200 transition-colors"
                    title="Archive Trip"
                  >
                    <Archive className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => handleDelete(trip.id, e)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                    title="Delete Trip"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <span className="font-bold text-forest-800 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                  Open Plan <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
