import React, { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import TransactionMonitor from './components/TransactionMonitor';
import FraudDashboard from './components/FraudDashboard';
import AlertsPanel from './components/AlertsPanel';
import PerformanceMetrics from './components/PerformanceMetrics';

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Establish WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
      setIsConnected(true);
      console.log('Connected to fraud detection system');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'dashboard_update') {
        setDashboardData(data.payload);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from fraud detection system');
    };

    // Fetch initial dashboard data
    fetchDashboardData();

    return () => {
      ws.close();
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/dashboard/stats');
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  return (
    <div className="app">
      <nav className="navbar navbar-dark bg-dark shadow">
        <div className="container-fluid">
          <span className="navbar-brand mb-0 h1">
            🛡️ Fraud Detection System
          </span>
          <div className="d-flex align-items-center">
            <span className={`badge ${isConnected ? 'bg-success' : 'bg-danger'} me-3`}>
              {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
            <span className="text-light">
              Real-time Monitoring Active
            </span>
          </div>
        </div>
      </nav>

      <div className="container-fluid mt-4">
        <div className="row">
          {/* Main Dashboard */}
          <div className="col-lg-8">
            <div className="row">
              <div className="col-12 mb-4">
                <FraudDashboard data={dashboardData} />
              </div>
              <div className="col-12 mb-4">
                <TransactionMonitor />
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="col-lg-4">
            <div className="row">
              <div className="col-12 mb-4">
                <AlertsPanel />
              </div>
              <div className="col-12 mb-4">
                <PerformanceMetrics />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

