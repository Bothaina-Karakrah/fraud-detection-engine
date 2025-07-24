// components/FraudDashboard.js - Real-time statistics display
import React from 'react';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

const FraudDashboard = ({ data }) => {
  if (!data) {
    return (
      <div className="card">
        <div className="card-body text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  const fraudRateData = {
    labels: ['Legitimate', 'Fraudulent'],
    datasets: [{
      data: [100 - data.fraud_rate, data.fraud_rate],
      backgroundColor: ['#28a745', '#dc3545'],
      hoverBackgroundColor: ['#34ce57', '#e55353']
    }]
  };

  return (
    <div className="card shadow">
      <div className="card-header bg-primary text-white">
        <h5 className="card-title mb-0">🎯 Fraud Detection Overview</h5>
      </div>
      <div className="card-body">
        <div className="row">
          {/* Key Metrics */}
          <div className="col-md-8">
            <div className="row">
              <div className="col-sm-6 mb-3">
                <div className="card bg-info text-white">
                  <div className="card-body text-center">
                    <h2 className="card-title">{data.total_transactions?.toLocaleString()}</h2>
                    <p className="card-text">Total Transactions</p>
                  </div>
                </div>
              </div>
              <div className="col-sm-6 mb-3">
                <div className="card bg-danger text-white">
                  <div className="card-body text-center">
                    <h2 className="card-title">{data.fraud_detected}</h2>
                    <p className="card-text">Fraud Detected</p>
                  </div>
                </div>
              </div>
              <div className="col-sm-6 mb-3">
                <div className="card bg-warning text-white">
                  <div className="card-body text-center">
                    <h2 className="card-title">{data.fraud_rate?.toFixed(2)}%</h2>
                    <p className="card-text">Fraud Rate</p>
                  </div>
                </div>
              </div>
              <div className="col-sm-6 mb-3">
                <div className="card bg-success text-white">
                  <div className="card-body text-center">
                    <h2 className="card-title">{data.transactions_per_hour}</h2>
                    <p className="card-text">Hourly Volume</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Fraud Rate Chart */}
          <div className="col-md-4">
            <h6 className="text-center mb-3">Fraud Distribution</h6>
            <Doughnut 
              data={fraudRateData} 
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'bottom'
                  }
                }
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default FraudDashboard;

