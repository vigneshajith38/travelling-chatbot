import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, PhoneCall, Building2, AlertTriangle, 
  FileText, CheckCircle2, MapPin, HeartPulse
} from 'lucide-react';
import { api } from '../../services/api';

export default function SafetyPanel({ destination = 'Munnar, Kerala' }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSafety() {
      setLoading(true);
      try {
        const data = await api.getSafetyReport(destination);
        setReport(data);
      } catch (err) {
        console.error('Safety report error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchSafety();
  }, [destination]);

  if (loading) {
    return (
      <div className="p-8 text-center text-xs text-slate-500">
        Loading verified emergency numbers and local safety directories...
      </div>
    );
  }

  if (!report) return null;

  return (
    <div className="space-y-6">
      {/* Header Advisory Banner */}
      <div className="p-6 rounded-2xl bg-white border border-sand-200 shadow-soft-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-forest-700 font-semibold text-xs mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Destination Safety Index</span>
          </div>
          <h3 className="font-serif font-bold text-xl text-slate-900">
            {report.overall_safety_rating}
          </h3>
          <p className="text-xs text-slate-500 mt-1 max-w-lg">
            Emergency contacts verified with national registries. Follow localized guidelines below for a seamless trip.
          </p>
        </div>
        <div className="px-3.5 py-1.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold text-xs w-fit">
          Verified Safe Zone
        </div>
      </div>

      {/* Speed Dial Emergency Numbers */}
      <div className="p-5 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-4">
        <h4 className="font-serif font-bold text-slate-900 text-sm">Emergency Hotlines (One-Tap Speed Dial)</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {report.emergency_numbers?.map((em, idx) => (
            <a
              key={idx}
              href={`tel:${em.phone}`}
              className="p-3.5 rounded-xl bg-cream-50 hover:bg-forest-50 border border-sand-200 hover:border-forest-600 transition-all flex items-center justify-between group"
            >
              <div>
                <h5 className="font-bold text-xs text-slate-900 group-hover:text-forest-800">{em.service}</h5>
                <span className="text-[11px] text-slate-500 leading-tight block mt-0.5">{em.notes}</span>
              </div>
              <div className="p-2 rounded-xl bg-forest-800 text-sand-300 font-mono font-bold text-xs shrink-0 flex items-center gap-1 shadow-sm">
                <PhoneCall className="w-3.5 h-3.5" />
                <span>{em.phone}</span>
              </div>
            </a>
          ))}
        </div>
      </div>

      {/* Nearby Medical & Police Facilities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-5 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-3">
          <div className="flex items-center gap-2 text-rose-700 font-bold text-xs">
            <HeartPulse className="w-4 h-4" />
            <span>Nearest Verified Medical Center</span>
          </div>
          {report.local_facilities?.filter(f => f.type === 'Hospital').map((h, i) => (
            <div key={i} className="p-3 rounded-xl bg-cream-50 border border-sand-200 space-y-1 text-xs">
              <h5 className="font-bold text-slate-900">{h.name}</h5>
              <p className="text-slate-600 flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span>{h.address} ({h.distance})</span>
              </p>
              <span className="text-[10px] text-forest-700 font-semibold block">{h.hours}</span>
            </div>
          ))}
        </div>

        <div className="p-5 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-3">
          <div className="flex items-center gap-2 text-skycoast-600 font-bold text-xs">
            <Building2 className="w-4 h-4" />
            <span>Nearest Tourist Police Station</span>
          </div>
          {report.local_facilities?.filter(f => f.type === 'Police Station').map((p, i) => (
            <div key={i} className="p-3 rounded-xl bg-cream-50 border border-sand-200 space-y-1 text-xs">
              <h5 className="font-bold text-slate-900">{p.name}</h5>
              <p className="text-slate-600 flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span>{p.address} ({p.distance})</span>
              </p>
              <span className="text-[10px] text-forest-700 font-semibold block">{p.hours}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Guidelines & Legal Notice */}
      <div className="p-5 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-3">
        <h4 className="font-serif font-bold text-slate-900 text-sm">Essential Travel Guidelines</h4>
        <div className="space-y-2">
          {report.essential_guidelines?.map((guide, idx) => (
            <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-forest-700 shrink-0 mt-0.5" />
              <span>{guide}</span>
            </div>
          ))}
        </div>
        <p className="text-[11px] text-slate-400 italic pt-2 border-t border-sand-100">
          {report.disclaimer}
        </p>
      </div>
    </div>
  );
}

