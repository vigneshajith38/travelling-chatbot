import React, { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin, Navigation, Clock, ExternalLink, Layers, Crosshair, Calendar } from 'lucide-react';

// Fix Leaflet's default icon path issues in React / Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Vibrant, accessible day-wise marker color palette
const DAY_COLORS = [
  '#1b4332', // Day 1: Deep Forest Green
  '#0284c7', // Day 2: Sky Azure Blue
  '#d97706', // Day 3: Warm Amber
  '#7c3aed', // Day 4: Royal Violet
  '#dc2626', // Day 5: Ruby Crimson
  '#059669', // Day 6: Vivid Emerald
  '#b08968', // Day 7+: Sandstone Gold
  '#475569'  // Fallback
];

// Custom colored SVG pin markers with sequence numbers
const createCustomIcon = (number, color = '#1b4332', isSelected = false) => {
  const size = isSelected ? 38 : 32;
  const anchorY = isSelected ? 38 : 32;
  const anchorX = size / 2;
  
  return L.divIcon({
    html: `
      <div style="
        background-color: ${color};
        color: white;
        width: ${size}px;
        height: ${size}px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.35);
        border: ${isSelected ? '3px solid #fef08a' : '2px solid white'};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      ">
        <span style="transform: rotate(45deg); font-size: ${isSelected ? '13px' : '11px'}; font-weight: 800; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">
          ${number}
        </span>
      </div>
    `,
    className: 'custom-leaflet-marker',
    iconSize: [size, size],
    iconAnchor: [anchorX, anchorY],
    popupAnchor: [0, -anchorY]
  });
};

// Auto-resizes and fits bounds cleanly when markers update or map tab is opened
function AutoFitAndResizeView({ validActivities, triggerFit }) {
  const map = useMap();

  useEffect(() => {
    // Invalidate size immediately and after short delay to fix blank/gray tiles in tabs
    map.invalidateSize();
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 150);
    return () => clearTimeout(timer);
  }, [map]);

  useEffect(() => {
    if (!validActivities || validActivities.length === 0) return;

    if (validActivities.length === 1) {
      map.setView([validActivities[0].lat, validActivities[0].lng], 14, { animate: true });
    } else {
      const bounds = L.latLngBounds(validActivities.map(a => [a.lat, a.lng]));
      map.fitBounds(bounds, {
        padding: [45, 45],
        maxZoom: 15,
        animate: true
      });
    }
  }, [validActivities, map, triggerFit]);

  return null;
}

// Available map tile styles
const TILE_PROVIDERS = {
  voyager: {
    name: 'Street (Voyager)',
    url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  },
  satellite: {
    name: 'Satellite View',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
  },
  osm: {
    name: 'OpenStreetMap',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }
};

export default function InteractiveMap({ 
  activities = [], 
  defaultCenter = [28.6139, 77.2090], // Default New Delhi, India
  height = '420px',
  onSelectActivity
}) {
  const [activeTileKey, setActiveTileKey] = useState('voyager');
  const [selectedDayFilter, setSelectedDayFilter] = useState('all');
  const [fitTrigger, setFitTrigger] = useState(0);
  const [selectedActId, setSelectedActId] = useState(null);

  // Filter valid coordinates
  const allValidActivities = useMemo(() => {
    return (activities || []).filter(a => 
      a && typeof a.lat === 'number' && typeof a.lng === 'number' && 
      !isNaN(a.lat) && !isNaN(a.lng) && a.lat !== 0 && a.lng !== 0
    );
  }, [activities]);

  // Extract distinct days present in the activities
  const distinctDays = useMemo(() => {
    const daysSet = new Set();
    allValidActivities.forEach(a => {
      if (a.day_number) daysSet.add(a.day_number);
    });
    return Array.from(daysSet).sort((a, b) => a - b);
  }, [allValidActivities]);

  // Filter based on selected day
  const filteredActivities = useMemo(() => {
    if (selectedDayFilter === 'all') return allValidActivities;
    return allValidActivities.filter(a => a.day_number === Number(selectedDayFilter));
  }, [allValidActivities, selectedDayFilter]);

  // Compute polyline route coordinates
  const polylineCoords = useMemo(() => {
    return filteredActivities.map(a => [a.lat, a.lng]);
  }, [filteredActivities]);

  const initialCenter = allValidActivities.length > 0 
    ? [allValidActivities[0].lat, allValidActivities[0].lng] 
    : defaultCenter;

  const currentTile = TILE_PROVIDERS[activeTileKey] || TILE_PROVIDERS.voyager;

  return (
    <div className="relative rounded-2xl overflow-hidden border border-sand-300 shadow-soft-md bg-cream-100 flex flex-col" style={{ height }}>
      {/* Top Floating Control Bar */}
      <div className="absolute top-2.5 left-2.5 right-2.5 z-[1000] flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        {/* Left: Waypoint Counter & Recenter Button */}
        <div className="flex items-center gap-1.5 bg-white/95 backdrop-blur-md px-3 py-1.5 rounded-xl shadow-soft-md border border-sand-200 text-xs pointer-events-auto">
          <div className="flex items-center gap-1.5 font-bold text-forest-900">
            <Navigation className="w-3.5 h-3.5 text-forest-700" />
            <span>{filteredActivities.length} {filteredActivities.length === 1 ? 'Stop' : 'Stops'}</span>
          </div>

          <span className="text-slate-300">|</span>

          <button
            onClick={() => setFitTrigger(prev => prev + 1)}
            title="Recenter & Fit All Waypoints in View"
            className="flex items-center gap-1 text-[11px] font-semibold text-forest-700 hover:text-forest-900 hover:bg-forest-50 px-2 py-0.5 rounded-lg transition-colors"
          >
            <Crosshair className="w-3 h-3 text-forest-600" />
            <span>Fit View</span>
          </button>
        </div>

        {/* Right: Map Style Switcher (Street vs Satellite) */}
        <div className="flex items-center bg-white/95 backdrop-blur-md p-1 rounded-xl shadow-soft-md border border-sand-200 text-[11px] font-medium pointer-events-auto">
          <button
            onClick={() => setActiveTileKey('voyager')}
            className={`px-2.5 py-1 rounded-lg transition-all flex items-center gap-1 ${
              activeTileKey === 'voyager'
                ? 'bg-forest-800 text-white font-bold shadow-sm'
                : 'text-slate-600 hover:text-forest-900'
            }`}
          >
            <span>Street</span>
          </button>
          <button
            onClick={() => setActiveTileKey('satellite')}
            className={`px-2.5 py-1 rounded-lg transition-all flex items-center gap-1 ${
              activeTileKey === 'satellite'
                ? 'bg-forest-800 text-white font-bold shadow-sm'
                : 'text-slate-600 hover:text-forest-900'
            }`}
          >
            <Layers className="w-3 h-3" />
            <span>Satellite</span>
          </button>
        </div>
      </div>

      {/* Bottom Floating Day Filter Pills (if itinerary has multiple days) */}
      {distinctDays.length > 1 && (
        <div className="absolute bottom-3 left-3 right-3 z-[1000] flex items-center gap-1.5 overflow-x-auto py-1 px-2 bg-white/90 backdrop-blur-md rounded-xl shadow-soft-md border border-sand-200 pointer-events-auto scrollbar-thin">
          <div className="flex items-center gap-1 text-[11px] font-bold text-slate-700 mr-1 shrink-0">
            <Calendar className="w-3 h-3 text-forest-700" />
            <span>Filter:</span>
          </div>

          <button
            onClick={() => {
              setSelectedDayFilter('all');
              setFitTrigger(prev => prev + 1);
            }}
            className={`px-2.5 py-1 rounded-lg text-[10px] font-bold transition-all shrink-0 ${
              selectedDayFilter === 'all'
                ? 'bg-forest-800 text-white shadow-sm'
                : 'bg-cream-100 text-slate-600 hover:bg-cream-200 border border-sand-200'
            }`}
          >
            All Days ({allValidActivities.length})
          </button>

          {distinctDays.map(dayNum => {
            const dayColor = DAY_COLORS[(dayNum - 1) % DAY_COLORS.length];
            const isSelected = selectedDayFilter === String(dayNum);

            return (
              <button
                key={dayNum}
                onClick={() => {
                  setSelectedDayFilter(String(dayNum));
                  setFitTrigger(prev => prev + 1);
                }}
                className={`px-2.5 py-1 rounded-lg text-[10px] font-bold transition-all shrink-0 flex items-center gap-1.5 ${
                  isSelected
                    ? 'text-white shadow-sm'
                    : 'bg-white text-slate-700 hover:bg-cream-100 border border-sand-200'
                }`}
                style={isSelected ? { backgroundColor: dayColor } : {}}
              >
                <span 
                  className="w-2 h-2 rounded-full shrink-0" 
                  style={{ backgroundColor: isSelected ? 'white' : dayColor }} 
                />
                <span>Day {dayNum}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Main Map Container */}
      <MapContainer
        center={initialCenter}
        zoom={12}
        scrollWheelZoom={true}
        className="w-full h-full z-10"
      >
        <AutoFitAndResizeView 
          validActivities={filteredActivities} 
          triggerFit={fitTrigger} 
        />

        <TileLayer
          key={activeTileKey}
          attribution={currentTile.attribution}
          url={currentTile.url}
          maxZoom={19}
        />

        {/* High-visibility connecting route line */}
        {polylineCoords.length > 1 && (
          <Polyline
            positions={polylineCoords}
            color={selectedDayFilter === 'all' ? '#1b4332' : DAY_COLORS[(Number(selectedDayFilter) - 1) % DAY_COLORS.length]}
            weight={4}
            opacity={0.85}
            dashArray="6, 8"
          />
        )}

        {/* Dynamic Waypoint Pin Markers */}
        {filteredActivities.map((act, index) => {
          const dayIndex = (act.day_number || 1) - 1;
          const markerColor = DAY_COLORS[dayIndex % DAY_COLORS.length];
          const isSelected = selectedActId === (act.id || index);
          const icon = createCustomIcon(index + 1, markerColor, isSelected);

          // Google Maps Turn-by-Turn directions URL
          const gmapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${act.lat},${act.lng}`;

          return (
            <Marker
              key={act.id || `${act.lat}-${act.lng}-${index}`}
              position={[act.lat, act.lng]}
              icon={icon}
              eventHandlers={{
                click: () => {
                  setSelectedActId(act.id || index);
                  if (onSelectActivity) onSelectActivity(act);
                }
              }}
            >
              <Popup className="wanderwise-map-popup">
                <div className="p-1 min-w-[210px] max-w-[250px] space-y-1.5 font-sans">
                  {/* Badge Header: Day, Slot & Time */}
                  <div className="flex items-center justify-between gap-1">
                    <span 
                      className="px-2 py-0.5 rounded-full text-[9px] font-bold text-white uppercase tracking-wider"
                      style={{ backgroundColor: markerColor }}
                    >
                      {act.day_number ? `Day ${act.day_number} • ` : ''}{act.time_slot || 'Activity'}
                    </span>
                    <span className="text-[10px] text-slate-500 font-semibold flex items-center gap-1">
                      <Clock className="w-2.5 h-2.5" />
                      {act.time_str || 'Scheduled'}
                    </span>
                  </div>

                  {/* Activity Title */}
                  <h4 className="font-bold text-slate-900 text-xs leading-snug">
                    {act.title}
                  </h4>

                  {/* Location Name */}
                  <p className="text-[11px] text-slate-600 flex items-start gap-1">
                    <MapPin className="w-3 h-3 text-forest-700 shrink-0 mt-0.5" />
                    <span className="line-clamp-2">{act.location_name || 'Destination Highlight'}</span>
                  </p>

                  {/* Cost & Duration details */}
                  <div className="flex items-center justify-between text-[11px] pt-1.5 border-t border-slate-100 font-semibold">
                    <span className="text-forest-800 font-bold">
                      {act.estimated_cost ? `₹${Number(act.estimated_cost).toLocaleString()}` : 'Free'}
                    </span>
                    <span className="text-slate-500 font-normal">
                      {act.duration_mins ? `${act.duration_mins} mins` : 'Flexible'}
                    </span>
                  </div>

                  {/* Google Maps Directions Button */}
                  <a
                    href={gmapsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full mt-1.5 py-1 px-2 rounded-lg bg-forest-50 hover:bg-forest-100 text-forest-900 text-[10px] font-bold flex items-center justify-center gap-1 border border-forest-200 transition-colors"
                  >
                    <span>Navigate in Google Maps</span>
                    <ExternalLink className="w-2.5 h-2.5 text-forest-700" />
                  </a>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
