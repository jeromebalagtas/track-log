import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function planTrip(payload) {
  const { data } = await axios.post(`${API_BASE}/plan-trip/`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  return data;
}
