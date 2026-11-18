import React, { useState } from 'react';
import { 
  CheckSquare, Square, Plus, Trash2, Luggage, 
  Sparkles, CheckCircle2, ShieldAlert
} from 'lucide-react';

export default function PackingChecklist({
  items = [],
  onToggleItem,
  onAddItem,
  onDeleteItem
}) {
  const [newItemName, setNewItemName] = useState('');
  const [newCategory, setNewCategory] = useState('Clothing');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const categories = ['All', 'Clothing', 'Toiletries', 'Electronics', 'Documents', 'Medicines', 'Activity'];

  const filteredItems = selectedCategory === 'All'
    ? items
    : items.filter(it => it.category === selectedCategory);

  const totalItems = items.length;
  const packedCount = items.filter(it => it.is_packed).length;
  const packedPct = totalItems > 0 ? Math.round((packedCount / totalItems) * 100) : 0;

  const handleAdd = (e) => {
    e.preventDefault();
    if (!newItemName.trim()) return;
    onAddItem({
      item_name: newItemName.trim(),
      category: newCategory,
      quantity: 1,
      is_custom: true
    });
    setNewItemName('');
  };

  return (
    <div className="space-y-6">
      {/* Progress Header Card */}
      <div className="p-6 rounded-2xl bg-white border border-sand-200 shadow-soft-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-forest-700 font-semibold text-xs mb-1">
            <Luggage className="w-4 h-4" />
            <span>Smart Packing Assistant</span>
          </div>
          <h3 className="font-serif font-bold text-xl text-slate-900">
            {packedPct === 100 ? 'All Packed & Ready to Go!' : `${packedCount} of ${totalItems} Essentials Packed`}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Personalized list generated from your destination climate, duration, and activities.
          </p>
        </div>

        <div className="sm:w-56 shrink-0 space-y-2">
          <div className="flex justify-between text-xs font-bold text-slate-700">
            <span>Progress</span>
            <span className="text-forest-800">{packedPct}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden border border-sand-200">
            <div
              className="h-full bg-forest-700 rounded-full transition-all duration-300"
              style={{ width: `${packedPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Category Pills Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
              selectedCategory === cat
                ? 'bg-forest-800 text-white shadow-soft-sm'
                : 'bg-white hover:bg-cream-200 text-slate-700 border border-sand-300'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Add Custom Item Input */}
      <form onSubmit={handleAdd} className="p-3 rounded-2xl bg-white border border-sand-200 shadow-soft-sm flex flex-col sm:flex-row items-center gap-2">
        <input
          type="text"
          value={newItemName}
          onChange={(e) => setNewItemName(e.target.value)}
          placeholder="Add custom packing item (e.g. GoPro extra battery)..."
          className="flex-1 px-3.5 py-2 rounded-xl bg-cream-50 border border-sand-300 text-xs focus:ring-1 focus:ring-forest-600 focus:bg-white w-full"
        />
        <select
          value={newCategory}
          onChange={(e) => setNewCategory(e.target.value)}
          className="px-3 py-2 rounded-xl border border-sand-300 text-xs bg-white text-slate-700 w-full sm:w-auto"
        >
          {categories.filter(c => c !== 'All').map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <button
          type="submit"
          className="w-full sm:w-auto px-4 py-2 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Add Item</span>
        </button>
      </form>

      {/* Items Checklist Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {filteredItems.map((item) => (
          <div
            key={item.id}
            onClick={() => onToggleItem && onToggleItem(item.id)}
            className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between gap-3 group ${
              item.is_packed
                ? 'bg-cream-100/60 border-sand-300 text-slate-400 line-through'
                : 'bg-white border-sand-200 text-slate-800 hover:border-forest-600 shadow-soft-sm'
            }`}
          >
            <div className="flex items-center gap-3 overflow-hidden">
              <div className={`p-0.5 rounded ${item.is_packed ? 'text-forest-700' : 'text-slate-400'}`}>
                {item.is_packed ? <CheckSquare className="w-4 h-4 text-forest-700" /> : <Square className="w-4 h-4" />}
              </div>
              <div className="overflow-hidden">
                <span className="text-xs font-semibold block truncate">{item.item_name}</span>
                <span className="text-[10px] text-slate-400 font-medium">{item.category} (x{item.quantity})</span>
              </div>
            </div>

            {onDeleteItem && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteItem(item.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-500 transition-opacity"
                title="Remove Item"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

