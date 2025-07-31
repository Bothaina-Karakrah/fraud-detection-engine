import React, { useState } from 'react';

const TransactionMonitor = () => {
  const [form, setForm] = useState({
    user_id: '',
    merchant_id: '',
    amount: '',
    location_country: '',
    location_city: '',
    ip_address: '',
    user_agent: ''
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/transactions/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error submitting transaction:', error);
      alert("Failed to analyze transaction");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card shadow p-4">
      <h5 className="mb-3">Submit Transaction for Analysis</h5>
      <form onSubmit={handleSubmit}>
        <div className="row g-3">
          <div className="col-md-6">
            <input name="user_id" className="form-control" placeholder="User ID" required onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <input name="merchant_id" className="form-control" placeholder="Merchant ID" required onChange={handleChange} />
          </div>
          <div className="col-md-4">
            <input name="amount" type="number" className="form-control" placeholder="Amount" required onChange={handleChange} />
          </div>
          <div className="col-md-4">
            <input name="location_country" className="form-control" placeholder="Country" required onChange={handleChange} />
          </div>
          <div className="col-md-4">
            <input name="location_city" className="form-control" placeholder="City" required onChange={handleChange} />
          </div>
        </div>

        <div className="mt-3 text-end">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze Transaction'}
          </button>
        </div>
      </form>

      {result && (
        <div className="alert alert-info mt-4">
          <h6>Fraud Analysis Result</h6>
          <ul className="mb-0">
            <li><strong>Transaction ID:</strong> {result.transaction_id}</li>
            <li><strong>Fraud Score:</strong> {result.fraud_score}</li>
            <li><strong>Risk Level:</strong> {result.risk_level}</li>
            <li><strong>Recommendation:</strong> {result.recommendation}</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default TransactionMonitor;