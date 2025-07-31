import React, { useEffect, useState } from 'react';

function PerformanceMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simulate fetching performance metrics
  useEffect(() => {
    const fetchMetrics = () => {
      // Example metrics data; replace with real API call if available
      const sampleMetrics = {
        transactionsProcessed: 1250,
        fraudAlertsGenerated: 47,
        averageResponseTimeMs: 230,
        systemUptimePercent: 99.95,
      };

      setTimeout(() => {
        setMetrics(sampleMetrics);
        setLoading(false);
      }, 1200);
    };

    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="card p-3 bg-info-subtle">
        <h5>Loading performance metrics...</h5>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="card p-3 bg-info-subtle">
        <h5>No performance metrics available</h5>
      </div>
    );
  }

  return (
    <div className="card p-3 bg-info-subtle">
      <h5>Performance Metrics</h5>
      <ul className="list-group">
        <li className="list-group-item">Transactions Processed: {metrics.transactionsProcessed}</li>
        <li className="list-group-item">Fraud Alerts Generated: {metrics.fraudAlertsGenerated}</li>
        <li className="list-group-item">Average Response Time: {metrics.averageResponseTimeMs} ms</li>
        <li className="list-group-item">System Uptime: {metrics.systemUptimePercent}%</li>
      </ul>
    </div>
  );
}

export default PerformanceMetrics;