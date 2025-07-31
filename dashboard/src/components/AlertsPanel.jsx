import React, { useEffect, useState } from 'react';

function AlertsPanel() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Simulate fetching alerts data
  useEffect(() => {
    const fetchAlerts = () => {
      // Simulated data - replace with real API call if available
      const sampleAlerts = [
        { id: 1, message: 'High transaction amount detected' },
        { id: 2, message: 'Multiple login attempts from different IPs' },
        { id: 3, message: 'Unusual merchant activity detected' },
      ];

      setTimeout(() => {
        setAlerts(sampleAlerts);
        setLoading(false);
      }, 1500);
    };

    fetchAlerts();
  }, []);

  if (loading) {
    return (
      <div className="card p-3 bg-warning-subtle">
        <h5>Loading alerts...</h5>
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="card p-3 bg-warning-subtle">
        <h5>No alerts at this time</h5>
      </div>
    );
  }

  return (
    <div className="card p-3 bg-warning-subtle">
      <h5>Alerts Panel</h5>
      <ul className="list-group">
        {alerts.map((alert) => (
          <li key={alert.id} className="list-group-item list-group-item-warning">
            {alert.message}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AlertsPanel;