import { useState } from 'react';
import TripForm from './components/TripForm';
import RouteMap from './components/RouteMap';
import TripResults from './components/TripResults';
import { planTrip } from './api';
import './App.css';

export default function App() {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (form) => {
    setLoading(true);
    setError(null);
    try {
      const result = await planTrip(form);
      setPlan(result);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to plan trip');
      setPlan(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="hero">
        <div className="hero-inner">
          <p className="eyebrow">FMCSA Hours of Service</p>
          <h1>Track Log</h1>
          <p className="tagline">
            Plan compliant trips, visualize routes, and generate driver daily log sheets.
          </p>
        </div>
      </header>

      <main className="layout">
        <aside className="sidebar">
          <TripForm onSubmit={handleSubmit} loading={loading} />
          {error && <div className="error-banner">{error}</div>}
        </aside>

        <section className="content">
          {plan ? (
            <>
              <RouteMap plan={plan} />
              <TripResults plan={plan} />
            </>
          ) : (
            <div className="empty-state card">
              <h2>Ready to plan</h2>
              <p>
                Enter your current location, pickup, dropoff, and cycle hours. We&apos;ll compute
                FMCSA-compliant driving windows, rest breaks, fuel stops, and paper log grids.
              </p>
              <ul>
                <li>Property-carrying · 70 hr / 8 day</li>
                <li>11 hr drive · 14 hr window · 30 min break after 8 hr</li>
                <li>10 hr rest · fuel every 1,000 mi · 1 hr pickup/dropoff</li>
              </ul>
            </div>
          )}
        </section>
      </main>

      <footer>
        <small>
          Based on FMCSA Interstate Truck Driver&apos;s Guide to Hours of Service (April 2022) ·
          Routing via OSRM · Maps © OpenStreetMap
        </small>
      </footer>
    </div>
  );
}
