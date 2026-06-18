import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const stopColors = {
  start: '#2563eb',
  pickup: '#16a34a',
  dropoff: '#dc2626',
  fuel: '#ca8a04',
  rest: '#7c3aed',
};

function pin(color) {
  return L.divIcon({
    className: 'custom-pin',
    html: `<span style="background:${color};width:14px;height:14px;border-radius:50%;display:block;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4)"></span>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });
}

export default function RouteMap({ plan }) {
  if (!plan?.locations?.current || !plan?.locations?.dropoff) return null;

  const { locations, route_coordinates: route, stops, legs } = plan;
  const points = [
    [locations.current.lat, locations.current.lon],
    [locations.pickup.lat, locations.pickup.lon],
    [locations.dropoff.lat, locations.dropoff.lon],
  ];
  const center = [
    (locations.current.lat + locations.dropoff.lat) / 2,
    (locations.current.lon + locations.dropoff.lon) / 2,
  ];

  return (
    <div className="card map-card">
      <h2>Route Map</h2>
      <p className="subtitle">
        {plan.total_miles} mi · {plan.total_days} day(s) · {plan.cycle_hours_remaining}h remaining in 70/8 cycle
      </p>

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
        {route?.length > 0 && <Polyline positions={route} color="#2563eb" weight={4} opacity={0.85} />}
        {stops?.map((stop, i) => (
          <Marker
            key={i}
            position={[stop.lat, stop.lon]}
            icon={pin(stopColors[stop.type] || '#64748b')}
          >
            <Popup>
              <strong>{stop.name}</strong>
              <br />
              Type: {stop.type}
              {stop.arrival && (
                <>
                  <br />
                  Arrival: {new Date(stop.arrival).toLocaleString()}
                </>
              )}
            </Popup>
          </Marker>
        ))}
        {points.map((p, i) => (
          <Marker key={`pt-${i}`} position={p} icon={pin('#0f172a')} />
        ))}
      </MapContainer>
    </div>
  );
}
