import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { 
  Compass, Calendar, Users, Wallet, Share2, 
  Sparkles, CloudRain, ShieldCheck, Luggage, Sliders, 
  MapPin, Printer, Copy, Check, ChevronRight, AlertCircle, RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import InteractiveMap from '../components/maps/InteractiveMap';
import DayAccordion from '../components/itinerary/DayAccordion';
import BudgetAnalytics from '../components/budget/BudgetAnalytics';
import GroupCollaboration from '../components/group/GroupCollaboration';
import WhatIfSimulatorModal from '../components/simulator/WhatIfSimulatorModal';
import PackingChecklist from '../components/packing/PackingChecklist';
import SafetyPanel from '../components/safety/SafetyPanel';

export default function TripDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const defaultTab = queryParams.get('tab') || 'itinerary';

  const [trip, setTrip] = useState(null);
  const [activeTab, setActiveTab] = useState(defaultTab);
  const [loading, setLoading] = useState(true);
  const [weather, setWeather] = useState(null);
  const [budgetSummary, setBudgetSummary] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [packingItems, setPackingItems] = useState([]);
  const [groupVotes, setGroupVotes] = useState([]);
  const [groupSettlements, setGroupSettlements] = useState(null);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [showSimulator, setShowSimulator] = useState(false);
  const [copiedShare, setCopiedShare] = useState(false);

  // Expanded days state
  const [expandedDays, setExpandedDays] = useState({ 1: true });

  const loadTripData = async () => {
    setLoading(true);
    try {
      const data = await api.getTripDetail(id);
      setTrip(data);
      setExpenses(data.expenses || []);
      setPackingItems(data.packing_items || []);

      // Load budget summary
      const bSummary = await api.getBudgetSummary(id);
      setBudgetSummary(bSummary);

      // Load weather for first activity coordinates or default destination coords
      const firstAct = data.itinerary_days?.[0]?.activities?.[0];
      const lat = firstAct?.lat || 10.0889;
      const lng = firstAct?.lng || 77.0595;
      const wData = await api.getWeather(lat, lng, 5);
      setWeather(wData);

      // Load group data if group trip
      if (data.is_group) {
        const vData = await api.getGroupVotes(id);
        setGroupVotes(vData);
        const sData = await api.getSettlements(id);
        setGroupSettlements(sData);
      }
    } catch (err) {
      console.error('Trip detail fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTripData();
  }, [id]);

  const toggleDay = (dayNum) => {
    setExpandedDays(prev => ({ ...prev, [dayNum]: !prev[dayNum] }));
  };

  const handleAddActivity = async (dayId, activityData) => {
    try {
      await api.addActivity(trip.id, dayId, activityData);
      await loadTripData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteActivity = async (activityId) => {
    try {
      await api.deleteActivity(activityId);
      await loadTripData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleWeatherReplan = async (dayNumber) => {
    try {
      await api.replanForWeather(trip.id, dayNumber, 'Rain');
      await loadTripData();
      alert(`Day ${dayNumber} outdoor activities swapped for sheltered indoor experiences!`);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddExpense = async (expData) => {
    try {
      await api.addExpense(trip.id, expData);
      await loadTripData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteExpense = async (expId) => {
    try {
      await api.deleteExpense(expId);
      await loadTripData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleTogglePacking = async (itemId) => {
    try {
      await api.togglePackingItem(itemId);
      setPackingItems(prev => prev.map(it => it.id === itemId ? { ...it, is_packed: !it.is_packed } : it));
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddPackingItem = async (itemData) => {
    try {
      const newItem = await api.addPackingItem(trip.id, itemData);
      setPackingItems(prev => [...prev, newItem]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeletePackingItem = async (itemId) => {
    try {
      await api.deletePackingItem(itemId);
      setPackingItems(prev => prev.filter(it => it.id !== itemId));
    } catch (err) {
      console.error(err);
    }
  };

  const handleInviteMember = async (memberData) => {
    try {
      await api.inviteGroupMember(trip.id, memberData);
      await loadTripData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleVote = async (voteData) => {
    try {
      await api.voteOnItem(trip.id, voteData);
      const vData = await api.getGroupVotes(trip.id);
      setGroupVotes(vData);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCopyShareLink = () => {
    const url = `${window.location.origin}/join/${trip?.share_code || 'TRIP'}`;
    navigator.clipboard.writeText(url);
    setCopiedShare(true);
    setTimeout(() => setCopiedShare(false), 2000);
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-3">
        <RefreshCw className="w-8 h-8 text-forest-700 animate-spin mx-auto" />
        <p className="text-xs text-slate-500 font-medium">Loading your smart trip itinerary & maps...</p>
      </div>
    );
  }

  if (!trip) {
    return (
      <div className="py-20 text-center space-y-3">
        <p className="text-sm text-slate-600">Trip not found.</p>
        <button onClick={() => navigate('/my-trips')} className="px-4 py-2 bg-forest-800 text-white rounded-xl text-xs">
          Back to My Trips
        </button>
      </div>
    );
  }

  // All activities flattened for the interactive map with explicit day_number
  const allActivities = trip.itinerary_days?.flatMap(d => (d.activities || []).map(a => ({ ...a, day_number: d.day_number }))) || [];

  return (
    <div className="space-y-6 pb-20">
      {/* 1. Master Trip Banner */}
      <div className="relative rounded-3xl overflow-hidden shadow-soft-xl border border-sand-300 min-h-[280px] flex items-end">
        <img
          src={trip.cover_image || 'https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1600&q=80'}
          alt={trip.title}
          className="absolute inset-0 w-full h-full object-cover object-center filter brightness-90"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-950 via-forest-950/50 to-transparent" />

        <div className="relative z-10 p-6 sm:p-8 w-full text-white flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-2.5 py-0.5 rounded-full bg-forest-700 text-sand-300 font-bold text-[10px] uppercase tracking-wider">
                {trip.status}
              </span>
              <span className="text-xs text-cream-200/90 font-medium flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-sand-300" />
                {trip.destination}
              </span>
              {trip.is_group && (
                <span className="px-2 py-0.5 rounded-full bg-skycoast-500/80 text-white text-[10px] font-bold">
                  Group Expedition
                </span>
              )}
            </div>

            <h1 className="font-serif font-bold text-2xl sm:text-3xl text-white">
              {trip.title}
            </h1>

            <div className="flex items-center gap-4 text-xs text-cream-300/80 font-medium flex-wrap">
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-sand-400" />
                {trip.start_date} → {trip.end_date}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Users className="w-3.5 h-3.5 text-sand-400" />
                {trip.travellers_count} Travellers
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Wallet className="w-3.5 h-3.5 text-sand-400" />
                ₹{trip.total_budget?.toLocaleString()} Budget
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => window.print()}
              className="p-2.5 rounded-xl bg-forest-900/80 hover:bg-forest-900 text-white backdrop-blur-md border border-white/20 text-xs font-semibold flex items-center gap-1.5 transition-colors"
              title="Print or Export Summary"
            >
              <Printer className="w-4 h-4 text-sand-300" />
              <span className="hidden sm:inline">Export PDF</span>
            </button>
            <button
              onClick={handleCopyShareLink}
              className="px-3.5 py-2.5 rounded-xl bg-forest-700 hover:bg-forest-600 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              {copiedShare ? <Check className="w-4 h-4 text-emerald-400" /> : <Share2 className="w-4 h-4 text-sand-300" />}
              <span>{copiedShare ? 'Copied!' : 'Share Trip'}</span>
            </button>
            <button
              onClick={() => setShowSimulator(true)}
              className="px-4 py-2.5 rounded-xl bg-sand-400 hover:bg-sand-300 text-forest-950 font-bold text-xs flex items-center gap-1.5 shadow-soft-sm transition-colors"
            >
              <Sliders className="w-4 h-4" />
              <span>Simulate</span>
            </button>
          </div>
        </div>
      </div>

      {/* 2. Command Center Tabs Navigation */}
      <div className="flex border-b border-sand-300 text-xs font-semibold overflow-x-auto gap-4 no-scrollbar">
        {[
          { id: 'itinerary', label: 'Itinerary & Interactive Map', icon: Compass },
          { id: 'weather', label: 'Live Weather & Replanning', icon: CloudRain },
          { id: 'budget', label: 'Budget & Expenses', icon: Wallet },
          { id: 'group', label: 'Group Collaboration', icon: Users },
          { id: 'packing', label: 'Smart Packing', icon: Luggage },
          { id: 'safety', label: 'Safety & Emergency', icon: ShieldCheck }
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 px-1 transition-colors border-b-2 whitespace-nowrap flex items-center gap-2 ${
                activeTab === tab.id
                  ? 'border-forest-800 text-forest-900 font-bold'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* 3. TAB CONTENT */}

      {/* TAB A: ITINERARY & INTERACTIVE MAP (Side by Side Desktop) */}
      {activeTab === 'itinerary' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left: Day Accordions (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center justify-between pb-1">
              <span className="text-xs text-slate-500 font-medium">
                {trip.itinerary_days?.length || 0} Days Planned • Geographic routing optimized
              </span>
              <button
                onClick={() => handleWeatherReplan(1)}
                className="text-xs text-forest-700 hover:text-forest-900 font-bold flex items-center gap-1"
              >
                <CloudRain className="w-3.5 h-3.5" />
                <span>Test Rainy-Day Swap</span>
              </button>
            </div>

            {trip.itinerary_days?.map((day) => (
              <DayAccordion
                key={day.id}
                day={day}
                isExpanded={!!expandedDays[day.day_number]}
                onToggle={() => toggleDay(day.day_number)}
                onAddActivity={handleAddActivity}
                onDeleteActivity={handleDeleteActivity}
                onRegenerateDay={handleWeatherReplan}
              />
            ))}
          </div>

          {/* Right: Interactive Map Sticky (5 cols) */}
          <div className="lg:col-span-5 sticky top-20">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-serif font-bold text-slate-900 text-sm">
                  Interactive Route Map
                </h4>
                <span className="text-[11px] text-forest-700 font-semibold">
                  {allActivities.length} Stops Connected
                </span>
              </div>
              <InteractiveMap
                activities={allActivities}
                height="560px"
                onSelectActivity={(act) => setSelectedActivity(act)}
              />
            </div>
          </div>
        </div>
      )}

      {/* TAB B: WEATHER & ADAPTIVE REPLANNING */}
      {activeTab === 'weather' && (
        <div className="space-y-6">
          {weather ? (
            <div className="space-y-6">
              {/* Current Weather Card */}
              <div className="p-6 rounded-3xl bg-white border border-sand-200 shadow-soft-sm flex flex-col sm:flex-row items-center justify-between gap-6">
                <div>
                  <div className="flex items-center gap-2 text-forest-700 font-semibold text-xs mb-1">
                    <CloudRain className="w-4 h-4" />
                    <span>Live Forecast: {weather.source}</span>
                  </div>
                  <h3 className="font-serif font-bold text-3xl text-slate-900">
                    {weather.current.temperature}°C
                  </h3>
                  <p className="text-xs font-bold text-forest-800 mt-0.5">
                    {weather.current.condition} (Feels like {weather.current.apparent_temperature}°C)
                  </p>
                  <p className="text-xs text-slate-500 mt-2 max-w-md leading-relaxed">
                    {weather.current.travel_tip}
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-cream-50 border border-sand-200 text-xs space-y-2 shrink-0 w-full sm:w-auto">
                  <div className="flex justify-between gap-6 text-slate-600">
                    <span>Rain Probability:</span>
                    <span className="font-bold text-slate-900">{weather.current.rain_probability}%</span>
                  </div>
                  <div className="flex justify-between gap-6 text-slate-600">
                    <span>Wind Speed:</span>
                    <span className="font-bold text-slate-900">{weather.current.wind_speed} km/h</span>
                  </div>
                </div>
              </div>

              {/* Dynamic Weather Replanner Trigger Card */}
              <div className="p-6 rounded-3xl bg-forest-900 text-cream-100 shadow-soft-md space-y-4 border border-forest-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-sand-300" />
                    <h4 className="font-serif font-bold text-base text-white">
                      Weather-Based Dynamic Itinerary Adaptation
                    </h4>
                  </div>
                  <span className="text-[10px] uppercase font-bold text-sand-300 bg-forest-800 px-2 py-0.5 rounded-full border border-forest-700">
                    Active AI Monitor
                  </span>
                </div>
                <p className="text-xs text-cream-300/80 leading-relaxed max-w-2xl">
                  If rainfall or severe weather affects outdoor scenic viewpoints or treks, WanderWise shifts them into cozy indoor tea museums, artisanal roast lounges, and covered cultural bazaars.
                </p>

                <div className="flex flex-wrap gap-3 pt-1">
                  <button
                    onClick={() => handleWeatherReplan(1)}
                    className="px-4 py-2.5 rounded-xl bg-sand-400 hover:bg-sand-300 text-forest-950 font-bold text-xs flex items-center gap-1.5 transition-colors"
                  >
                    <CloudRain className="w-4 h-4" />
                    <span>Adapt Day 1 for Rain (Indoor Swaps)</span>
                  </button>
                  <button
                    onClick={() => handleWeatherReplan(2)}
                    className="px-4 py-2.5 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-bold text-xs flex items-center gap-1.5 border border-forest-700 transition-colors"
                  >
                    <CloudRain className="w-4 h-4 text-sand-300" />
                    <span>Adapt Day 2 for Rain</span>
                  </button>
                </div>
              </div>

              {/* 5-Day Daily Forecast Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {weather.daily?.map((d, i) => (
                  <div key={i} className="p-4 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-2">
                    <div className="flex justify-between items-center text-xs font-semibold text-slate-500">
                      <span>{d.date}</span>
                      <span className="text-forest-700 font-bold">{d.max_temp}° / {d.min_temp}°</span>
                    </div>
                    <span className="font-bold text-slate-800 text-xs block">{d.weather_condition}</span>
                    <p className="text-[11px] text-slate-500 leading-snug">{d.travel_tip}</p>
                    <div className="pt-2 border-t border-sand-100 text-[10px] text-slate-400 flex justify-between">
                      <span>Rain Risk</span>
                      <span className="font-semibold text-slate-700">{d.rain_probability}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500">Loading weather forecast data...</p>
          )}
        </div>
      )}

      {/* TAB C: BUDGET & EXPENSES */}
      {activeTab === 'budget' && (
        <BudgetAnalytics
          summary={budgetSummary}
          expenses={expenses}
          onAddExpense={handleAddExpense}
          onDeleteExpense={handleDeleteExpense}
          currency={trip.budget_currency}
        />
      )}

      {/* TAB D: GROUP COLLABORATION */}
      {activeTab === 'group' && (
        <GroupCollaboration
          trip={trip}
          members={trip.members}
          votes={groupVotes}
          settlements={groupSettlements}
          onInviteMember={handleInviteMember}
          onVote={handleVote}
        />
      )}

      {/* TAB E: SMART PACKING CHECKLIST */}
      {activeTab === 'packing' && (
        <PackingChecklist
          items={packingItems}
          onToggleItem={handleTogglePacking}
          onAddItem={handleAddPackingItem}
          onDeleteItem={handleDeletePackingItem}
        />
      )}

      {/* TAB F: SAFETY & EMERGENCY ASSISTANT */}
      {activeTab === 'safety' && (
        <SafetyPanel destination={trip.destination} />
      )}

      {/* What-If Simulator Modal */}
      <WhatIfSimulatorModal
        trip={trip}
        isOpen={showSimulator}
        onClose={() => setShowSimulator(false)}
        onApplyChanges={async (simRes) => {
          await api.updateTrip(trip.id, {
            total_budget: simRes.new_cost
          });
          await loadTripData();
          alert('Simulated budget updates applied successfully!');
        }}
      />
    </div>
  );
}
