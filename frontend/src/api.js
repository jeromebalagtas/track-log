import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export function formatApiError(err) {
  const data = err?.response?.data;
  if (typeof data?.error === 'string') return data.error;
  if (typeof data === 'string') return data;
  if (data && typeof data === 'object') {
    try {
      return JSON.stringify(data);
    } catch {
      return 'Request failed';
    }
  }
  return err?.message || 'Failed to plan trip';
}

export async function planTrip(payload) {
  const { data } = await axios.post(`${API_BASE}/plan-trip`, payload, {
    headers: { 'Content-Type': 'application/json' },
    timeout: 55000,
  });
  return data;
}
