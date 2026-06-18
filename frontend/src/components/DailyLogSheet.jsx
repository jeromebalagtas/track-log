import { useState } from 'react';
import { downloadLogSheetImage } from '../utils/downloadLogSheet';

const STATUS_ROWS = [
  { key: 'off_duty', label: 'Off Duty' },
  { key: 'sleeper_berth', label: 'Sleeper Berth' },
  { key: 'driving', label: 'Driving' },
  { key: 'on_duty', label: 'On Duty (not driving)' },
];

const HOURS = Array.from({ length: 24 }, (_, i) => i);

function timeToMinutes(iso) {
  const d = new Date(iso);
  return d.getHours() * 60 + d.getMinutes();
}

function segmentOnHour(seg, hour) {
  const start = timeToMinutes(seg.start);
  const end = timeToMinutes(seg.end);
  const hStart = hour * 60;
  const hEnd = (hour + 1) * 60;
  if (end <= hStart || start >= hEnd) return false;
  if (seg.end <= seg.start) return start < hEnd; // crosses midnight edge
  return true;
}

function quarterFilled(seg, hour, quarter) {
  const start = timeToMinutes(seg.start);
  let end = timeToMinutes(seg.end);
  if (end <= start) end += 24 * 60;
  const qStart = hour * 60 + quarter * 15;
  const qEnd = qStart + 15;
  let s = start;
  let e = end;
  if (e > 24 * 60) {
    // normalize for same-day grid display
    e = Math.min(e, 24 * 60);
  }
  return e > qStart && s < qEnd;
}

export default function DailyLogSheet({ log, index }) {
  const [downloading, setDownloading] = useState(false);
  const date = new Date(log.date);
  const month = date.toLocaleString('en-US', { month: 'short' });
  const day = date.getDate();
  const year = date.getFullYear();
  const sheetId = `log-sheet-${index}`;

  const segmentsByStatus = STATUS_ROWS.map((row) =>
    log.segments.filter((s) => s.status === row.key),
  );

  const handleDownloadImage = async () => {
    const element = document.getElementById(sheetId);
    if (!element) return;

    setDownloading(true);
    try {
      const safeDate = log.date || `day-${index + 1}`;
      await downloadLogSheetImage(element, `track-log-${safeDate}.png`);
    } catch {
      window.alert('Image download failed. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="log-sheet card" id={sheetId}>
      <div className="log-header">
        <h3>Driver&apos;s Daily Log (24 hours)</h3>
        <div className="log-header-actions">
          <div className="log-date">
            <span>{month}</span>
            <span>{day}</span>
            <span>{year}</span>
          </div>
          <button
            type="button"
            className="log-download-btn"
            onClick={handleDownloadImage}
            disabled={downloading}
          >
            {downloading ? 'Saving…' : 'Download as PNG'}
          </button>
        </div>
      </div>

      <div className="log-meta">
        <div><strong>From:</strong> {log.from_location}</div>
        <div><strong>To:</strong> {log.to_location}</div>
        <div><strong>Total Miles Driving Today:</strong> {log.driving_miles}</div>
        <div><strong>Total Mileage Today:</strong> {log.total_miles}</div>
      </div>

      <div className="grid-wrapper">
        <table className="hos-grid" aria-label={`HOS grid day ${index + 1}`}>
          <thead>
            <tr>
              <th className="status-col">Status</th>
              {HOURS.map((h) => (
                <th key={h} colSpan={4} className="hour-label">
                  {h === 0 ? 'Mid' : h <= 12 ? h : h - 12}
                  {h === 0 ? 'night' : h < 12 ? ' AM' : h === 12 ? ' Noon' : ' PM'}
                </th>
              ))}
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {STATUS_ROWS.map((row, ri) => (
              <tr key={row.key}>
                <td className="status-label">{row.label}</td>
                {HOURS.map((hour) =>
                  [0, 1, 2, 3].map((q) => {
                    const active = segmentsByStatus[ri].some((seg) =>
                      quarterFilled(seg, hour, q),
                    );
                    return (
                      <td
                        key={`${hour}-${q}`}
                        className={`grid-cell ${active ? 'filled' : ''} status-${row.key}`}
                      />
                    );
                  }),
                )}
                <td className="total-cell">{log.totals[row.key] ?? 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="remarks">
        <strong>Remarks</strong>
        <ul>
          {log.remarks?.length ? (
            log.remarks.map((r, i) => <li key={i}>{r}</li>)
          ) : (
            <li>Enter name of place you reported and where released from work and when and where each change of duty occurred.</li>
          )}
        </ul>
      </div>

      <div className="recap">
        <div className="recap-block">
          <strong>70 Hour / 8 Day — Recap</strong>
          <div>A. Total on duty last 7 days incl. today: <strong>{log.recap.a_last_7_days}</strong></div>
          <div>B. Total hours available tomorrow (70 − A): <strong>{log.recap.b_available_tomorrow_70}</strong></div>
          <div>C. Total on duty last 8 days incl. today: <strong>{log.recap.c_last_8_days}</strong></div>
          <div>Daily on duty (lines 3 &amp; 4): <strong>{log.recap.daily_on_duty}</strong></div>
        </div>
      </div>
    </div>
  );
}
