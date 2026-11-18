import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin, Navigation, Clock, Tag } from 'lucide-react';

// Fix Leaflet's default icon path issues in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom colored SVG pin markers
const createCustomIcon = (number, color = '#1b4332') => {
  return L.divIcon({
    html: `
      <div style="
        background-color: ${color};
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border: 2px solid white;
      ">
        <span style="transform: rotate(45deg); font-size: 12px; font-weight: bold; font-family: sans-serif;">
          ${number}
        </span>
      </div>
    `,
    className: 'custom-leaflet-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
  });
};

function ChangeMapView({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.setView(center, zoom || 13, { animate: true });
    }
  }, [center, zoom, map]);
  return null;
}

export default function InteractiveMap({ 
  activities = [], 
  defaultCenter = [10.0889, 77.0595],
  height = '420px',
  onSelectActivity
}) {
  const validActivities = activities.filter(a => a.lat && a.lng && !isNaN(a.lat) && !isNaN(a.lng));
  
  const center = validActivities.length > 0 
    ? [validActivities[0].lat, validActivities[0].lng] 
    : defaultCenter;

  const polylineCoords = validActivities.map(a => [a.lat, a.lng]);

  const categoryColors = {
    nature: '#2d6a4f',
    culture: '#b08968',
    food: '#d97706',
    photo: '#0284c7',
    adventure: '#dc2626',
    relaxation: '#059669',
    shopping: '#7c3aed'
  };

  return (
    <div className="relative rounded-2xl overflow-hidden border border-sand-300 shadow-soft-md bg-cream-200" style={{ height }}>
      {/* Route Info Badge Header Overlay */}
      <div className="absolute top-3 left-3 z-[1000] bg-white/95 backdrop-blur-md px-3.5 py-2 rounded-xl shadow-soft-md border border-sand-200 flex items-center gap-3 text-xs">
        <div className="flex items-center gap-1.5 font-semibold text-forest-900">
          <Navigation className="w-3.5 h-3.5 text-forest-700" />
          <span>{validActivities.length} Waypoints</span>
        </div>
        <span className="text-slate-300">|</span>
        <span className="text-slate-600 font-medium">OpenStreetMap & OSRM Engine</span>
      </div>

      <MapContainer
        center={center}
        zoom={12}
        scrollWheelZoom={false}
        className="w-full h-full z-10"
      >
        <ChangeMapView center={center} zoom={12} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Connecting Route Line */}
        {polylineCoords.length > 1 && (
          <Polyline
            positions={polylineCoords}
            color="#2d6a4f"
            weight={4}
            opacity={0.8}
            dashArray="6, 8"
          />
        )}

        {/* Activity Markers */}
        {validActivities.map((act, index) => {
          const color = categoryColors[act.category?.toLowerCase()] || '#1b4332';
          const icon = createCustomIcon(index + 1, color);

          return (
            <Marker
              key={act.id || index}
              position={[act.lat, act.lng]}
              icon={icon}
              eventHandlers={{
                click: () => onSelectActivity && onSelectActivity(act)
              }}
            >
              <Popup className="wanderwise-map-popup">
                <div className="p-1 max-w-[220px]">
                  <div className="flex items-center gap-1.5 mb-1">
                    <span 
                      className="px-2 py-0.5 rounded-full text-[10px] font-semibold text-white uppercase tracking-wider"
                      style={{ backgroundColor: color }}
                    >
                      {act.time_slot || 'Activity'}
                    </span>
                    <span className="text-[11px] text-slate-500 font-medium">{act.time_str}</span>
                  </div>
                  <h4 className="font-bold text-slate-900 text-xs leading-tight mb-1">{act.title}</h4>
                  <p className="text-[11px] text-slate-600 flex items-center gap-1 mb-1">
                    <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                    <span className="truncate">{act.location_name}</span>
                  </p>
                  <div className="flex items-center justify-between text-[11px] pt-1.5 border-t border-slate-100 font-semibold">
                    <span className="text-forest-700">₹{act.estimated_cost || 0}</span>
                    <span className="text-slate-500 font-normal">{act.duration_mins} mins</span>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}

