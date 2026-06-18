import { useState } from 'react';
import DailyLogSheet from './DailyLogSheet';
import { downloadTripReport } from '../utils/downloadReport';

export default function TripResults({ plan }) {
  const [downloading, setDownloading] = useState(false);

  if (!plan) return null;

  const handleDownload = async () => {
    setDownloading(true);
    try {
      await downloadTripReport(`track-log-${plan.daily_logs[0]?.date || 'trip'}.pdf`);
    } catch {
      window.alert('Download failed. Please try again or use Print (Ctrl+P) on this page.');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="results">
      <div className="results-toolbar">
        <button type="button" className="download-btn" onClick={handleDownload} disabled={downloading}>
          {downloading ? 'Preparing PDF…' : 'Download Map & Logs (PDF)'}
        </button>
      </div>

      <div className="card instructions-card">
        <h2>Route Instructions</h2>
        <ol>
          {plan.instructions.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </div>

      <div className="logs-section" id="daily-logs-section">
        <h2>Daily Log Sheets ({plan.daily_logs.length})</h2>
        {plan.daily_logs.map((log, i) => (
          <DailyLogSheet key={log.date} log={log} index={i} />
        ))}
      </div>
    </div>
  );
}
