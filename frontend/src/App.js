import React, { useState, useRef, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const UploadPage = () => {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

  const handleFileUpload = async (file) => {
    if (!file) return;
    
    setIsUploading(true);
    setUploadStatus(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_BASE_URL}/api/ingest`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setUploadStatus({
        type: 'success',
        message: 'CSV file processed successfully!',
        details: { imported: response.data.imported }
      });
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: 'Upload failed: ' + (error.response?.data?.detail || error.message)
      });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
      <h2>📁 CSV Upload</h2>
      <div style={{ border: '2px dashed #ddd', borderRadius: '8px', padding: '3rem', textAlign: 'center', backgroundColor: '#f9f9f9' }}>
        <input ref={fileInputRef} type="file" accept=".csv" onChange={handleFileChange} style={{ display: 'none' }} />
        <p>Upload your transaction CSV files here</p>
        <button 
          style={{ backgroundColor: isUploading ? '#ccc' : '#0066cc', color: 'white', border: 'none', padding: '0.75rem 1.5rem', borderRadius: '4px', cursor: isUploading ? 'not-allowed' : 'pointer' }}
          disabled={isUploading}
          onClick={() => fileInputRef.current?.click()}
        >
          {isUploading ? 'Processing...' : 'Choose CSV File'}
        </button>
      </div>

      {uploadStatus && (
        <div style={{ marginTop: '2rem', padding: '1rem', borderRadius: '4px', backgroundColor: uploadStatus.type === 'success' ? '#d4edda' : '#f8d7da' }}>
          <h4>{uploadStatus.type === 'success' ? '✅ Success!' : '❌ Error'}</h4>
          <p>{uploadStatus.message}</p>
          {uploadStatus.details && (
            <p>Imported: {uploadStatus.details.imported} transactions</p>
          )}
          {uploadStatus.type === 'success' && (
            <Link to="/reconcile" style={{ backgroundColor: '#28a745', color: 'white', padding: '0.5rem 1rem', textDecoration: 'none', borderRadius: '4px', display: 'inline-block' }}>
              View Transactions →
            </Link>
          )}
        </div>
      )}
    </div>
  );
};

const ReconcilePage = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/reconcile/inbox`);
        setTransactions(response.data.transactions || []);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, []);

  if (loading) return <div style={{ padding: '2rem' }}>Loading...</div>;

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
      <h2>🔄 AI Reconciliation ({transactions.length} transactions)</h2>
      
      {transactions.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p>No transactions found. Upload a CSV file to get started.</p>
          <Link to="/upload">Upload CSV File →</Link>
        </div>
      ) : (
        <div>
          {transactions.map((t, i) => (
            <div key={i} style={{ backgroundColor: '#f8f9fa', padding: '1rem', marginBottom: '1rem', borderRadius: '4px' }}>
              <h4>{t.description}</h4>
              <p><strong>Amount:</strong> ${t.amount}</p>
              <p><strong>Category:</strong> {t.category}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const ForecastPage = () => {
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    const fetchForecast = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/forecast`);
        setForecastData(response.data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchForecast();
  }, []);

  if (loading) return <div style={{ padding: '2rem' }}>Loading forecast...</div>;

  const currentCash = forecastData?.current_cash || 0;
  const businessMetrics = forecastData?.business_metrics || {};
  const projections = forecastData?.daily_projections || [];

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
      <h2>📊 Cash Flow Forecast</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ backgroundColor: currentCash >= 0 ? '#e8f5e8' : '#ffeaa7', padding: '1rem', borderRadius: '4px' }}>
          <h4>Current Balance</h4>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>${currentCash.toFixed(2)}</p>
        </div>
        <div style={{ backgroundColor: '#e8f4fd', padding: '1rem', borderRadius: '4px' }}>
          <h4>8-Week Projection</h4>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>
            ${projections.length > 0 ? projections[projections.length - 1].projected_balance.toFixed(2) : '0.00'}
          </p>
        </div>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h4>Business Metrics</h4>
        <p>Total Inflows: ${businessMetrics.total_inflows?.toFixed(2) || '0.00'}</p>
        <p>Total Outflows: ${businessMetrics.total_outflows?.toFixed(2) || '0.00'}</p>
        <p>Net Flow: ${businessMetrics.net_flow?.toFixed(2) || '0.00'}</p>
      </div>

      {projections.length > 0 && (
        <div>
          <h4>Weekly Projections</h4>
          {projections.slice(0, 4).map((proj, i) => (
            <div key={i} style={{ padding: '0.5rem', borderBottom: '1px solid #eee' }}>
              Week {proj.week}: ${proj.projected_balance.toFixed(2)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const HomePage = () => (
  <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem', textAlign: 'center' }}>
    <h1>🏦 BannkMint AI</h1>
    <p>SMB Banking Operating System with AI-powered transaction reconciliation</p>
    <Link to="/upload" style={{ backgroundColor: '#0066cc', color: 'white', padding: '1rem 2rem', textDecoration: 'none', borderRadius: '4px', display: 'inline-block', marginTop: '2rem' }}>
      Get Started →
    </Link>
  </div>
);

function App() {
  return (
    <Router>
      <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
        <nav style={{ backgroundColor: 'white', padding: '1rem', borderBottom: '1px solid #ddd' }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center', gap: '2rem' }}>
            <Link to="/" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#333', textDecoration: 'none' }}>🏦 BannkMint AI</Link>
            <Link to="/upload" style={{ color: '#333', textDecoration: 'none' }}>Upload</Link>
            <Link to="/reconcile" style={{ color: '#333', textDecoration: 'none' }}>Reconcile</Link>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/reconcile" element={<ReconcilePage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;