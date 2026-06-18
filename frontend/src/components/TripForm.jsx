import { useState } from 'react';

const DEFAULTS = {
  current_location: 'Chicago, IL',
  pickup_location: 'Indianapolis, IN',
  dropoff_location: 'Columbus, OH',
  cycle_used_hours: 0,
};

export default function TripForm({ onSubmit, loading }) {
  const [form, setForm] = useState(DEFAULTS);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === 'cycle_used_hours' ? parseFloat(value) || 0 : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form className="trip-form card" onSubmit={handleSubmit}>
      <h2>Trip Details</h2>
      <p className="subtitle">Enter locations and current 70-hour cycle usage</p>

      <label>
        Current Location
        <input name="current_location" value={form.current_location} onChange={handleChange} required />
      </label>

      <label>
        Pickup Location
        <input name="pickup_location" value={form.pickup_location} onChange={handleChange} required />
      </label>

      <label>
        Dropoff Location
        <input name="dropoff_location" value={form.dropoff_location} onChange={handleChange} required />
      </label>

      <label>
        Current Cycle Used (hours)
        <input
          type="number"
          name="cycle_used_hours"
          min="0"
          max="70"
          step="0.5"
          value={form.cycle_used_hours}
          onChange={handleChange}
        />
      </label>

      <button type="submit" disabled={loading}>
        {loading ? 'Planning trip…' : 'Plan Trip & Generate Logs'}
      </button>
    </form>
  );
}
