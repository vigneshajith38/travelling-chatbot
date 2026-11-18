import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Wallet, TrendingUp, AlertTriangle, CheckCircle, 
  ArrowRight, PieChart as PieIcon, Plus
} from 'lucide-react';
import { useTrip } from '../context/TripContext';
import { api } from '../services/api';

export default function Budget() {
  const navigate = useNavigate();
  const { trips } = useTrip();
  const [selectedTripId, setSelectedTripId] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (trips.length > 0 && !selectedTripId) {
      setSelectedTripId(trips[0].id);
    }
  }, [trips]);

  useEffect(() => {
    if (selectedTripId) {
      loadSummary(selectedTripId);
    }
  }, [selectedTripId]);

  const loadSummary = async (tripId) => {
    setLoading(true);
    try {
      const data = await api.getBudgetSummary(tripId);
      setSummary(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const activeTrip = trips.find(t => t.id === selectedTripId);

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-forest-700 font-semibold text-xs mb-1">
            <Wallet className="w-4 h-4" />
            <span>Financial Travel Planning</span>
          </div>
          <h1 className="font-serif font-bold text-2xl sm:text-3xl text-slate-900">
            Smart Budget Tracker & Analyzer
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Monitor real-time spending across transportation, boutique stays, cafes, and activities.
          </p>
        </div>

        {/* Trip Selector Dropdown */}
        {trips.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-semibold">Active Trip:</span>
            <select
              value={selectedTripId || ''}
              onChange={(e) => setSelectedTripId(parseInt(e.target.value))}
              className="px-3.5 py-2 rounded-xl bg-white border border-sand-300 text-xs font-bold text-forest-900 shadow-soft-sm"
            >
              {trips.map(t => (
                <option key={t.id} value={t.id}>{t.title}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {summary && (
        <div className="space-y-6">
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div className="p-6 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-1">
              <span className="text-xs text-slate-500 font-medium">Total Allocated Budget</span>
              <h3 className="font-serif font-bold text-2xl text-slate-900">
                ₹{summary.total_budget?.toLocaleString()}
              </h3>
              <p className="text-[11px] text-slate-400">
                ₹{summary.per_person_budget?.toLocaleString()} per traveller allowance
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-1">
              <span className="text-xs text-slate-500 font-medium">Actual Spent So Far</span>
              <h3 className="font-serif font-bold text-2xl text-forest-800">
                ₹{summary.total_actual_spent?.toLocaleString()}
              </h3>
              <p className="text-[11px] text-slate-400">
                {summary.spending_percentage}% of total allowance used
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-1">
              <span className="text-xs text-slate-500 font-medium">Remaining Safe Buffer</span>
              <h3 className={`font-serif font-bold text-2xl ${
                summary.remaining_budget < 0 ? 'text-rose-600' : 'text-emerald-700'
              }`}>
                ₹{summary.remaining_budget?.toLocaleString()}
              </h3>
              <p className="text-[11px] text-slate-400">
                {summary.remaining_budget < 0 ? 'Attention: over budget' : 'Comfortable cushion'}
              </p>
            </div>
          </div>

          {/* Category Budget Breakdown Table */}
          <div className="p-6 rounded-3xl bg-white border border-sand-200 shadow-soft-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-serif font-bold text-base text-slate-900">
                Category Spending Allocations
              </h3>
              {activeTrip && (
                <button
                  onClick={() => navigate(`/trips/${activeTrip.id}?tab=budget`)}
                  className="text-xs font-bold text-forest-800 hover:text-forest-900 flex items-center gap-1"
                >
                  <span>Open Itemized Receipts</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-sand-200 text-slate-500 font-semibold">
                    <th className="py-2.5 px-3">Expense Category</th>
                    <th className="py-2.5 px-3 text-right">Target Allocation</th>
                    <th className="py-2.5 px-3 text-right">Spent to Date</th>
                    <th className="py-2.5 px-3 text-right">Remaining</th>
                    <th className="py-2.5 px-3 text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sand-100">
                  {summary.categories?.map((cat) => (
                    <tr key={cat.category} className="hover:bg-cream-50/70">
                      <td className="py-3 px-3 font-semibold text-slate-900">{cat.category}</td>
                      <td className="py-3 px-3 text-right font-medium text-slate-600">
                        ₹{cat.allocated?.toLocaleString()} ({cat.percentage}%)
                      </td>
                      <td className="py-3 px-3 text-right font-bold text-forest-800">
                        ₹{cat.spent?.toLocaleString()}
                      </td>
                      <td className={`py-3 px-3 text-right font-semibold ${
                        cat.remaining < 0 ? 'text-rose-600' : 'text-emerald-700'
                      }`}>
                        ₹{cat.remaining?.toLocaleString()}
                      </td>
                      <td className="py-3 px-3 text-center">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          cat.status === 'Safe' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                        }`}>
                          {cat.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="text-[11px] text-slate-400 italic pt-2 border-t border-sand-100">
              {summary.pricing_notice}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
