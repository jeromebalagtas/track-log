import DailyLogSheet from './DailyLogSheet';

export default function TripResults({ plan }) {
  if (!plan) return null;

  return (
    <div className="results">
      <div className="card instructions-card">
        <h2>Route Instructions</h2>
        <ol>
          {plan.instructions.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </div>

      <div className="logs-section" id="daily-logs-section">
        <h2 className="logs-section-title">Daily Log Sheets ({plan.daily_logs.length})</h2>
        {plan.daily_logs.map((log, i) => (
          <DailyLogSheet key={log.date} log={log} index={i} />
        ))}
      </div>
    </div>
  );
}
