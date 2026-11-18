import React, { useState, useEffect } from 'react';
import { 
  Sliders, ArrowRight, CheckCircle2, AlertCircle, Sparkles, 
  Train, Plane, Car, Users, Calendar, Wallet, X
} from 'lucide-react';
import { api } from '../../services/api';

export default function WhatIfSimulatorModal({
  trip,
  isOpen,
  onClose,
  onApplyChanges
}) {
  const [extraDays, setExtraDays] = useState(0);
  const [budgetChange, setBudgetChange] = useState(0);
  const [transportMode, setTransportMode] = useState('driving');
  const [extraFriends, setExtraFriends] = useState(0);
  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (trip && isOpen) {
      runSimulation();
    }
  }, [trip, extraDays, budgetChange, transportMode, extraFriends, isOpen]);

  const runSimulation = async () => {
    if (!trip) return;
    setLoading(true);
    try {
      const res = await api.simulateTrip(trip.id, {
        extra_days: extraDays,
        budget_change: budgetChange,
        transport_mode: transportMode,
        extra_travellers: extraFriends
      });
      setSimResult(res);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl border border-sand-300 max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-150 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-sand-200 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-forest-800 text-sand-300 flex items-center justify-center shadow-sm">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-serif font-bold text-lg text-slate-900">What-If Trip Simulator</h3>
              <p className="text-xs text-slate-500">Test hypothetical scenarios before committing changes to your real itinerary.</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-cream-200 text-slate-400 hover:text-slate-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Controls Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
          {/* Trip Duration Slider */}
          <div className="p-4 rounded-2xl bg-cream-50 border border-sand-200 space-y-2">
            <div className="flex items-center justify-between font-semibold text-slate-700">
              <span className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-forest-700" />
                Trip Duration
              </span>
              <span className="px-2 py-0.5 rounded-md bg-forest-100 text-forest-800 font-bold">
                {extraDays >= 0 ? `+${extraDays} Days` : `${extraDays} Days`}
              </span>
            </div>
            <input
              type="range"
              min="-1"
              max="4"
              step="1"
              value={extraDays}
              onChange={(e) => setExtraDays(parseInt(e.target.value))}
              className="w-full accent-forest-700 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>-1 Day</span>
              <span>Baseline</span>
              <span>+4 Days</span>
            </div>
          </div>

          {/* Friends Joining */}
          <div className="p-4 rounded-2xl bg-cream-50 border border-sand-200 space-y-2">
            <div className="flex items-center justify-between font-semibold text-slate-700">
              <span className="flex items-center gap-1.5">
                <Users className="w-4 h-4 text-forest-700" />
                Additional Friends
              </span>
              <span className="px-2 py-0.5 rounded-md bg-forest-100 text-forest-800 font-bold">
                +{extraFriends} Friends
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="4"
              step="1"
              value={extraFriends}
              onChange={(e) => setExtraFriends(parseInt(e.target.value))}
              className="w-full accent-forest-700 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>Just Me/Current</span>
              <span>+2</span>
              <span>+4 Friends</span>
            </div>
          </div>

          {/* Transportation Mode Toggle */}
          <div className="p-4 rounded-2xl bg-cream-50 border border-sand-200 space-y-2 sm:col-span-2">
            <span className="font-semibold text-slate-700 block mb-1">Transit Mode Switcher</span>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'driving', name: 'Road Trip / Cab', icon: Car },
                { id: 'train', name: 'Scenic Train', icon: Train },
                { id: 'flight', name: 'Express Air', icon: Plane }
              ].map((m) => {
                const Icon = m.icon;
                return (
                  <button
                    key={m.id}
                    onClick={() => setTransportMode(m.id)}
                    className={`p-2.5 rounded-xl border flex flex-col items-center gap-1 font-semibold transition-all ${
                      transportMode === m.id
                        ? 'bg-forest-800 text-white border-forest-800 shadow-sm'
                        : 'bg-white text-slate-700 border-sand-300 hover:bg-cream-100'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-[11px]">{m.name}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Live Simulation Output Box */}
        {simResult && (
          <div className="p-5 rounded-2xl bg-forest-900 text-cream-100 space-y-3.5 shadow-soft-md">
            <div className="flex items-center justify-between border-b border-forest-800 pb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-sand-300" />
                <span className="font-serif font-bold text-sm text-white">Simulated Impact Summary</span>
              </div>
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                simResult.feasibility_status === 'Within Budget'
                  ? 'bg-emerald-900/60 text-emerald-300 border border-emerald-600'
                  : 'bg-amber-900/60 text-amber-300 border border-amber-600'
              }`}>
                {simResult.feasibility_status}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="p-2.5 rounded-xl bg-forest-800/80">
                <span className="text-[10px] text-cream-400 block">New Estimated Total</span>
                <span className="font-serif font-bold text-base text-sand-300">
                  ₹{simResult.new_cost?.toLocaleString()}
                </span>
              </div>
              <div className="p-2.5 rounded-xl bg-forest-800/80">
                <span className="text-[10px] text-cream-400 block">Net Difference</span>
                <span className={`font-serif font-bold text-base ${
                  simResult.cost_difference > 0 ? 'text-rose-300' : 'text-emerald-300'
                }`}>
                  {simResult.cost_difference >= 0 ? `+₹${simResult.cost_difference?.toLocaleString()}` : `-₹${Math.abs(simResult.cost_difference)?.toLocaleString()}`}
                </span>
              </div>
              <div className="p-2.5 rounded-xl bg-forest-800/80">
                <span className="text-[10px] text-cream-400 block">Per-Person Cost</span>
                <span className="font-serif font-bold text-base text-white">
                  ₹{simResult.per_person_cost?.toLocaleString()}
                </span>
              </div>
            </div>

            <div className="space-y-1.5 text-xs text-cream-200/90 pt-1">
              <p className="font-semibold text-sand-300">• {simResult.transport_impact}</p>
              {simResult.recommendations?.map((rec, i) => (
                <p key={i}>• {rec}</p>
              ))}
            </div>
          </div>
        )}

        {/* Modal Actions */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2.5 rounded-xl text-slate-600 hover:bg-cream-200 text-xs font-semibold"
          >
            Discard Simulation
          </button>
          <button
            onClick={() => {
              if (onApplyChanges && simResult) {
                onApplyChanges(simResult);
              }
              onClose();
            }}
            className="px-5 py-2.5 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-bold text-xs flex items-center gap-2 shadow-soft-sm transition-all"
          >
            <CheckCircle2 className="w-4 h-4 text-sand-300" />
            <span>Apply Simulated Changes</span>
          </button>
        </div>
      </div>
    </div>
  );
}

