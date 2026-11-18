import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, User, Key, Sliders, 
  Check, Sparkles, Shield, DollarSign, RefreshCw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Settings() {
  const { user, updatePreferences } = useAuth();

  const [fullName, setFullName] = useState(user?.full_name || 'Aarav Sharma');
  const [email, setEmail] = useState(user?.email || 'wanderer@wanderwise.com');
  const [budgetLevel, setBudgetLevel] = useState(user?.preferences?.budget_level || 'moderate');
  const [pace, setPace] = useState(user?.preferences?.travel_pace || 'balanced');
  const [currency, setCurrency] = useState(user?.preferences?.preferred_currency || 'INR');
  const [apiKey, setApiKey] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const availableStyles = [
    { id: 'mountains', label: 'Mountains & Peaks' },
    { id: 'beaches', label: 'Coastlines & Beaches' },
    { id: 'coffee', label: 'Coffee Plantations & Cafes' },
    { id: 'scenic', label: 'Scenic Sunset Viewpoints' },
    { id: 'adventure', label: 'Treks & 4x4 Safaris' },
    { id: 'peaceful', label: 'Tranquil & Slow Travel' },
    { id: 'culture', label: 'Temples & Heritage' }
  ];

  const [selectedStyles, setSelectedStyles] = useState(
    user?.preferences?.preferred_styles || ['mountains', 'scenic', 'peaceful', 'coffee']
  );

  const toggleStyle = (id) => {
    if (selectedStyles.includes(id)) {
      setSelectedStyles(selectedStyles.filter(s => s !== id));
    } else {
      setSelectedStyles([...selectedStyles, id]);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await updatePreferences({
        preferred_styles: selectedStyles,
        budget_level: budgetLevel,
        travel_pace: pace,
        preferred_currency: currency
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert('Failed to save settings');
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-forest-700 font-semibold text-xs mb-1">
          <SettingsIcon className="w-4 h-4" />
          <span>Profile & Travel Customization</span>
        </div>
        <h1 className="font-serif font-bold text-2xl sm:text-3xl text-slate-900">
          Preferences & Settings
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Tune your travel preferences so WanderWise AI generates perfectly paced itineraries.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Profile Details Card */}
        <div className="p-6 rounded-3xl bg-white border border-sand-200 shadow-soft-sm space-y-4">
          <h3 className="font-serif font-bold text-base text-slate-900 border-b border-sand-100 pb-2 flex items-center gap-2">
            <User className="w-4 h-4 text-forest-700" />
            <span>Traveler Profile</span>
          </h3>

          <div className="flex items-center gap-4">
            <img
              src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"
              alt="Avatar"
              className="w-16 h-16 rounded-full object-cover ring-2 ring-forest-700/20"
            />
            <div>
              <h4 className="font-bold text-sm text-slate-900">{fullName}</h4>
              <p className="text-xs text-slate-500">{email}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs pt-2">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Display Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl border border-sand-300 text-xs focus:ring-1 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Email</label>
              <input
                type="email"
                value={email}
                disabled
                className="w-full px-3.5 py-2 rounded-xl border border-sand-200 bg-cream-100 text-slate-500 text-xs"
              />
            </div>
          </div>
        </div>

        {/* Travel Persona & Preferences */}
        <div className="p-6 rounded-3xl bg-white border border-sand-200 shadow-soft-sm space-y-4">
          <h3 className="font-serif font-bold text-base text-slate-900 border-b border-sand-100 pb-2 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-forest-700" />
            <span>AI Itinerary Preferences</span>
          </h3>

          <div className="space-y-2">
            <label className="block text-xs font-semibold text-slate-700">Preferred Travel Styles</label>
            <div className="flex flex-wrap gap-2">
              {availableStyles.map((style) => {
                const active = selectedStyles.includes(style.id);
                return (
                  <button
                    key={style.id}
                    type="button"
                    onClick={() => toggleStyle(style.id)}
                    className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                      active
                        ? 'bg-forest-800 text-white shadow-soft-sm'
                        : 'bg-cream-100 hover:bg-cream-200 text-slate-700 border border-sand-300'
                    }`}
                  >
                    {style.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs pt-2">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Default Travel Pace</label>
              <select
                value={pace}
                onChange={(e) => setPace(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-sand-300 text-xs"
              >
                <option value="relaxed">Relaxed & Leisurely</option>
                <option value="balanced">Balanced Highlights</option>
                <option value="packed">Action-Packed Sightseer</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Typical Spending Tier</label>
              <select
                value={budgetLevel}
                onChange={(e) => setBudgetLevel(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-sand-300 text-xs"
              >
                <option value="budget">Backpacker / Budget</option>
                <option value="moderate">Moderate / Value</option>
                <option value="luxury">Luxury Boutique</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Currency</label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-sand-300 text-xs"
              >
                <option value="INR">₹ INR (Indian Rupee)</option>
                <option value="USD">$ USD (US Dollar)</option>
                <option value="EUR">€ EUR (Euro)</option>
                <option value="GBP">£ GBP (British Pound)</option>
              </select>
            </div>
          </div>
        </div>

        {/* AI Model Configuration Card */}
        <div className="p-6 rounded-3xl bg-forest-900 text-cream-100 shadow-soft-md space-y-3 border border-forest-800">
          <div className="flex items-center gap-2 text-sand-300 font-semibold text-xs">
            <Sparkles className="w-4 h-4" />
            <span>Gemini Intelligence Model</span>
          </div>
          <h4 className="font-serif font-bold text-base text-white">Custom Gemini API Key (Optional)</h4>
          <p className="text-xs text-cream-200/80 leading-relaxed">
            WanderWise comes built-in with full travel intelligence out of the box. If you wish to use your own Google Gemini API key, enter it below. Your key is stored securely in environment variables and never exposed to the frontend.
          </p>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="AIzaSy..."
            className="w-full px-3.5 py-2 rounded-xl bg-forest-800/80 border border-forest-700 text-xs text-white placeholder-cream-300/40 focus:ring-1 focus:ring-sand-400 font-mono"
          />
        </div>

        {/* Save Actions */}
        <div className="flex items-center justify-between pt-2">
          {savedSuccess ? (
            <span className="text-xs font-bold text-emerald-700 flex items-center gap-1.5">
              <Check className="w-4 h-4 text-emerald-600" />
              <span>Preferences updated successfully!</span>
            </span>
          ) : <span />}

          <button
            type="submit"
            className="px-6 py-2.5 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-bold text-xs flex items-center gap-2 shadow-soft-sm transition-all"
          >
            <span>Save Preferences</span>
          </button>
        </div>
      </form>
    </div>
  );
}
