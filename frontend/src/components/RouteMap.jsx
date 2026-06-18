import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const MARKER_STYLES = {
  start: { label: 'A', color: '#2563eb', title: 'Current / Start' },
  pickup: { label: 'P', color: '#16a34a', title: 'Pickup' },
  dropoff: { label: 'D', color: '#dc2626', title: 'Dropoff' },
  fuel: { label: 'F', color: '#ca8a04', title: 'Fuel Stop' },
  rest: { label: 'R', color: '#7c3aed', title: 'Rest' },
};

function labeledPin(type) {
  const style = MARKER_STYLES[type] || { label: '•', color: '#64748b', title: type };
  return L.divIcon({
    className: 'map-marker-wrap',
    html: `
      <div class="map-marker" style="--marker-color:${style.color}" title="${style.title}">
        <span class="map-marker-label">${style.label}</span>
        <span class="map-marker-pin"></span>
      </div>
    `,
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -40],
  });
}

function locationMarkers(locations) {
  const items = [];
  if (locations?.current?.lat != null) {
    items.push({ key: 'current', loc: locations.current, type: 'start' });
  }
  if (locations?.pickup?.lat != null && !locations.pickup.is_na) {
    items.push({ key: 'pickup', loc: locations.pickup, type: 'pickup' });
  }
  if (locations?.dropoff?.lat != null && !locations.dropoff.is_na) {
    items.push({ key: 'dropoff', loc: locations.dropoff, type: 'dropoff' });
  }
  return items;
}

export default function RouteMap({ plan }) {
  if (!plan?.locations) return null;

  const { locations, route_coordinates: route, stops, legs } = plan;
  const markers = locationMarkers(locations);

  if (markers.length === 0) return null;

  const lats = markers.map((m) => m.loc.lat);
  const lons = markers.map((m) => m.loc.lon);
  const center = [
    (Math.min(...lats) + Math.max(...lats)) / 2,
    (Math.min(...lons) + Math.max(...lons)) / 2,
  ];

  return (
    <div className="card map-card" id="route-map-section">
      <h2>Route Map</h2>
      <p className="subtitle">
        {plan.total_miles} mi · {plan.total_days} day(s) · {plan.cycle_hours_remaining}h remaining in 70/8 cycle
      </p>

      <div className="map-legend">
        <span><i className="legend-dot start" /> A Current</span>
        <span><i className="legend-dot pickup" /> P Pickup</span>
        <span><i className="legend-dot dropoff" /> D Dropoff</span>
        <span><i className="legend-dot fuel" /> F Fuel</span>
        <span><i className="legend-dot rest" /> R Rest</span>
      </div>

      <div className="leg-summary">
        {legs?.map((leg, i) => (
          <span key={i} className="leg-chip">
            {leg.from} → {leg.to}: <strong>{leg.miles} mi</strong>
          </span>
        ))}
      </div>

      <MapContainer center={center} zoom={6} className="map-container" scrollWheelZoom>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {route?.length > 0 && <Polyline positions={route} color="#38bdf8" weight={5} opacity={0.9} />}
        {markers.map(({ key, loc, type }) => (
          <Marker key={key} position={[loc.lat, loc.lon]} icon={labeledPin(type)}>
            <Popup>
              <strong>{MARKER_STYLES[type].title}</strong>
              <br />
              {loc.full_name || loc.name}
            </Popup>
          </Marker>
        ))}
        {stops
          ?.filter((s) => s.type === 'fuel' || s.type === 'rest')
          .map((stop, i) => (
            <Marker key={`stop-${i}`} position={[stop.lat, stop.lon]} icon={labeledPin(stop.type)}>
              <Popup>
                <strong>{MARKER_STYLES[stop.type]?.title || stop.type}</strong>
                <br />
                {stop.name}
              </Popup>
            </Marker>
          ))}
      </MapContainer>
    </div>
  );
}
