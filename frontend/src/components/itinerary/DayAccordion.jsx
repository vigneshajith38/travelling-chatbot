import React, { useState } from 'react';
import { 
  Clock, MapPin, Navigation, Plus, Trash2, Edit2, 
  ChevronDown, ChevronUp, Sparkles, CloudRain, ShieldCheck, Footprints, Car, Bus
} from 'lucide-react';

export default function DayAccordion({
  day,
  isExpanded = true,
  onToggle,
  onAddActivity,
  onDeleteActivity,
  onEditActivity,
  onRegenerateDay
}) {
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newLoc, setNewLoc] = useState('');
  const [newTime, setNewTime] = useState('11:00 AM');
  const [newCost, setNewCost] = useState('0');
  const [newSlot, setNewSlot] = useState('afternoon');

  const slotIcons = {
    walking: Footprints,
    driving: Car,
    transit: Bus
  };

  const handleCreateActivity = (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    onAddActivity(day.id, {
      title: newTitle.trim(),
      location_name: newLoc.trim() || newTitle.trim(),
      time_slot: newSlot,
      time_str: newTime,
      lat: day.activities[0]?.lat || 10.0889,
      lng: day.activities[0]?.lng || 77.0595,
      estimated_cost: parseFloat(newCost) || 0,
      duration_mins: 90,
      travel_time_from_prev: '15 mins',
      transport_mode: 'walking',
      category: 'sightseeing',
      is_indoor: false,
      order_index: day.activities.length
    });
    setNewTitle('');
    setNewLoc('');
    setShowAddModal(false);
  };

  return (
    <div className="bg-white rounded-2xl border border-sand-200/80 shadow-soft-sm overflow-hidden transition-all mb-4">
      {/* Day Accordion Header */}
      <div 
        onClick={onToggle}
        className="p-4 sm:p-5 flex items-center justify-between cursor-pointer hover:bg-cream-50/80 transition-colors border-b border-sand-100"
      >
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-forest-800 text-white flex flex-col items-center justify-center font-serif font-bold text-sm shrink-0 shadow-sm">
            <span>D{day.day_number}</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-serif font-bold text-slate-900 text-sm sm:text-base">
                {day.title}
              </h3>
              <span className="text-xs text-slate-500 font-medium">({day.date})</span>
            </div>
            <p className="text-xs text-forest-700 font-semibold mt-0.5">{day.theme}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onRegenerateDay && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRegenerateDay(day.day_number);
              }}
              className="px-2.5 py-1.5 rounded-lg bg-cream-200 hover:bg-cream-300 text-forest-900 text-xs font-semibold flex items-center gap-1 transition-colors"
              title="Regenerate Day"
            >
              <Sparkles className="w-3.5 h-3.5 text-forest-700" />
              <span className="hidden sm:inline">Regenerate</span>
            </button>
          )}
          <div className="text-slate-400 p-1">
            {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </div>
        </div>
      </div>

      {/* Accordion Content */}
      {isExpanded && (
        <div className="p-4 sm:p-6 space-y-4 bg-cream-50/40">
          {day.notes && (
            <div className="p-3 rounded-xl bg-sand-100/60 border border-sand-200 text-xs text-slate-700 leading-relaxed flex items-start gap-2">
              <span className="font-bold text-forest-800 shrink-0">AI Travel Note:</span>
              <span>{day.notes}</span>
            </div>
          )}

          {/* Activities List */}
          <div className="space-y-3 relative before:absolute before:inset-0 before:left-5 before:w-0.5 before:bg-sand-300 before:z-0">
            {day.activities.map((act, idx) => {
              const TransportIcon = slotIcons[act.transport_mode] || Footprints;
              return (
                <div key={act.id || idx} className="relative z-10 flex items-start gap-3.5 group">
                  {/* Step circle indicator */}
                  <div className="w-10 h-10 rounded-full bg-forest-50 border-2 border-forest-700 text-forest-800 font-bold text-xs flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                    {idx + 1}
                  </div>

                  {/* Activity Card */}
                  <div className="flex-1 p-3.5 sm:p-4 rounded-xl bg-white border border-sand-200 shadow-soft-sm hover:shadow-soft-md transition-all">
                    <div className="flex items-start justify-between gap-2 mb-1.5">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-forest-100 text-forest-800">
                          {act.time_slot}
                        </span>
                        <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
                          <Clock className="w-3 h-3 text-slate-400" />
                          {act.time_str}
                        </span>
                        {act.is_indoor && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-skycoast-50 text-skycoast-600 border border-skycoast-200">
                            Indoor Venue
                          </span>
                        )}
                      </div>

                      {/* Delete Action */}
                      <button
                        onClick={() => onDeleteActivity && onDeleteActivity(act.id)}
                        className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-500 transition-opacity"
                        title="Delete Activity"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <h4 className="font-bold text-slate-900 text-sm mb-1">{act.title}</h4>
                    <p className="text-xs text-slate-600 leading-relaxed mb-2.5">{act.description}</p>

                    <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-sand-100 flex-wrap gap-2">
                      <div className="flex items-center gap-1 text-slate-700 font-medium">
                        <MapPin className="w-3.5 h-3.5 text-forest-700" />
                        <span>{act.location_name}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="flex items-center gap-1 text-slate-500">
                          <TransportIcon className="w-3.5 h-3.5 text-sand-500" />
                          <span>{act.travel_time_from_prev}</span>
                        </span>
                        <span className="font-bold text-forest-800">
                          ₹{act.estimated_cost?.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Add Activity Button */}
          {!showAddModal ? (
            <button
              onClick={() => setShowAddModal(true)}
              className="w-full py-2.5 rounded-xl border border-dashed border-sand-400 hover:border-forest-600 text-slate-600 hover:text-forest-800 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors bg-white/60"
            >
              <Plus className="w-4 h-4 text-forest-700" />
              <span>Add Custom Activity to Day {day.day_number}</span>
            </button>
          ) : (
            <form onSubmit={handleCreateActivity} className="p-4 rounded-xl bg-white border border-sand-300 shadow-soft-sm space-y-3">
              <h4 className="font-bold text-xs text-slate-800">Add New Activity</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Activity Name</label>
                  <input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g. Sunset Tea Tasting"
                    className="w-full px-3 py-1.5 rounded-lg border border-sand-300 text-xs focus:ring-1 focus:ring-forest-600"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Location</label>
                  <input
                    type="text"
                    value={newLoc}
                    onChange={(e) => setNewLoc(e.target.value)}
                    placeholder="e.g. Lockhart Terrace"
                    className="w-full px-3 py-1.5 rounded-lg border border-sand-300 text-xs focus:ring-1 focus:ring-forest-600"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Time Slot</label>
                  <select
                    value={newSlot}
                    onChange={(e) => setNewSlot(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg border border-sand-300 text-xs"
                  >
                    <option value="morning">Morning</option>
                    <option value="afternoon">Afternoon</option>
                    <option value="evening">Evening</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Estimated Cost (₹)</label>
                  <input
                    type="number"
                    value={newCost}
                    onChange={(e) => setNewCost(e.target.value)}
                    placeholder="0"
                    className="w-full px-3 py-1.5 rounded-lg border border-sand-300 text-xs"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1.5 rounded-lg text-slate-600 text-xs hover:bg-cream-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-3.5 py-1.5 rounded-lg bg-forest-800 hover:bg-forest-700 text-white font-semibold text-xs"
                >
                  Save Activity
                </button>
              </div>
            </form>
          )}
        </div>
      )}
    </div>
  );
}

