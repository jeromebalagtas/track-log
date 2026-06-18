const NA_VALUES = new Set(['n/a', 'na', 'none', '-']);

export function isNA(value) {
  return NA_VALUES.has(String(value || '').trim().toLowerCase());
}

export function validateTripForm(form) {
  const errors = {};

  const current = String(form.current_location || '').trim();
  const pickup = String(form.pickup_location || '').trim();
  const dropoff = String(form.dropoff_location || '').trim();
  const cycleRaw = String(form.cycle_used_hours ?? '').trim();

  if (!current) {
    errors.current_location = 'Current location is required.';
  } else if (isNA(current)) {
    errors.current_location = 'Current location cannot be N/A.';
  }

  if (!pickup) {
    errors.pickup_location = 'Pickup location is required (use N/A if not applicable).';
  }

  if (!dropoff) {
    errors.dropoff_location = 'Dropoff location is required (use N/A if not applicable).';
  }

  if (isNA(pickup) && isNA(dropoff)) {
    errors.pickup_location = 'At least pickup or dropoff must be a real city.';
    errors.dropoff_location = 'At least pickup or dropoff must be a real city.';
  }

  if (cycleRaw === '') {
    errors.cycle_used_hours = 'Enter hours used in your 70-hour cycle (0–70).';
  } else if (!/^\d+(\.\d+)?$/.test(cycleRaw)) {
    errors.cycle_used_hours = 'Cycle hours must be a number.';
  } else {
    const hours = parseFloat(cycleRaw);
    if (hours < 0 || hours > 70) {
      errors.cycle_used_hours = 'Cycle hours must be between 0 and 70.';
    }
  }

  return errors;
}

export function hasErrors(errors) {
  return Object.keys(errors).length > 0;
}

export function firstError(errors) {
  return Object.values(errors)[0] || null;
}
