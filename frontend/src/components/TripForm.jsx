import { useState } from 'react';
import { hasErrors, validateTripForm } from '../utils/validation';

const DEFAULTS = {
  current_location: 'Chicago, IL',
  pickup_location: 'Indianapolis, IN',
  dropoff_location: 'Columbus, OH',
  cycle_used_hours: '0',
};

export default function TripForm({ onSubmit, loading }) {
  const [form, setForm] = useState(DEFAULTS);
  const [fieldErrors, setFieldErrors] = useState({});
  const [alert, setAlert] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
    setAlert(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const errors = validateTripForm(form);
    if (hasErrors(errors)) {
      setFieldErrors(errors);
      setAlert(Object.values(errors)[0]);
      return;
    }

    onSubmit({
      ...form,
      cycle_used_hours: parseFloat(form.cycle_used_hours),
    });
  };

  return (
    <form className="trip-form card" onSubmit={handleSubmit} noValidate>
      <h2>Trip Details</h2>
      <p className="subtitle">Enter locations and current 70-hour cycle usage. Use N/A for optional pickup or dropoff.</p>

      {alert && <div className="alert-banner" role="alert">{alert}</div>}

      <label className={fieldErrors.current_location ? 'has-error' : ''}>
        Current Location
        <input
          name="current_location"
          value={form.current_location}
          onChange={handleChange}
          placeholder="City, ST"
          autoComplete="off"
        />
        {fieldErrors.current_location && <span className="field-error">{fieldErrors.current_location}</span>}
      </label>

      <label className={fieldErrors.pickup_location ? 'has-error' : ''}>
        Pickup Location
        <input
          name="pickup_location"
          value={form.pickup_location}
          onChange={handleChange}
          placeholder="City, ST or N/A"
          autoComplete="off"
        />
        {fieldErrors.pickup_location && <span className="field-error">{fieldErrors.pickup_location}</span>}
      </label>

      <label className={fieldErrors.dropoff_location ? 'has-error' : ''}>
        Dropoff Location
        <input
          name="dropoff_location"
          value={form.dropoff_location}
          onChange={handleChange}
          placeholder="City, ST or N/A"
          autoComplete="off"
        />
        {fieldErrors.dropoff_location && <span className="field-error">{fieldErrors.dropoff_location}</span>}
      </label>

      <label className={fieldErrors.cycle_used_hours ? 'has-error' : ''}>
        Current Cycle Used (hours)
        <input
          type="text"
          inputMode="decimal"
          name="cycle_used_hours"
          className="cycle-input"
          value={form.cycle_used_hours}
          onChange={handleChange}
          placeholder="0 – 70"
          autoComplete="off"
        />
        {fieldErrors.cycle_used_hours && <span className="field-error">{fieldErrors.cycle_used_hours}</span>}
      </label>

      <button type="submit" disabled={loading}>
        {loading ? 'Planning trip…' : 'Plan Trip & Generate Logs'}
      </button>
    </form>
  );
}
