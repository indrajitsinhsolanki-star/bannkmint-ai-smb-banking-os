import React, { useState, useRef, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Simple Navigation Component
const Navigation = () => (
  <nav style={{ padding: '1rem', backgroundColor: '#f8f9fa', marginBottom: '2rem' }}>
    <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', gap: '2rem' }}>
      <Link to="/" style={{ color: '#0066cc', textDecoration: 'none', fontWeight: 'bold' }}>
        🏦 BannkMint AI
      </Link>
      <Link to="/upload" style={{ color: '#0066cc', textDecoration: 'none' }}>Upload</Link>
      <Link to="/reconcile" style={{ color: '#0066cc', textDecoration: 'none' }}>Reconcile</Link>
      <Link to="/forecast" style={{ color: '#0066cc', textDecoration: 'none' }}>Forecast</Link>
    </div>
  </nav>
);

// Home Page
const HomePage = () => (
  <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
    <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '1rem', color: '#333' }}>
        🏦 BannkMint AI SMB Banking OS
      </h1>
      <p style={{ fontSize: '1.5rem', color: '#666', marginBottom: '2rem' }}>
        v0.2.0 - Financial Intelligence Platform
      </p>
      <p style={{ fontSize: '1.1rem', color: '#888', maxWidth: '600px', margin: '0 auto' }}>
        AI-powered transaction categorization, cash flow forecasting, and professional financial reporting for SMBs.
      </p>
    </div>

    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginTop: '3rem' }}>
      <FeatureCard 
        title="🔄 AI Reconciliation"
        description="Intelligent transaction categorization with confidence scores and explanations"
        link="/reconcile"
      />
      <FeatureCard 
        title="📊 Cash Flow Forecasting"
        description="SMB-focused 4-8 week forecasting with crisis prevention alerts"
        link="/forecast"
      />
      <FeatureCard 
        title="📁 CSV Upload"
        description="Robust CSV ingestion with automatic categorization and deduplication"
        link="/upload"
      />
    </div>
  </div>
);

// Feature Card Component
const FeatureCard = ({ title, description, link }) => (
  <div style={{ 
    border: '1px solid #ddd', 
    borderRadius: '8px', 
    padding: '1.5rem', 
    backgroundColor: 'white',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  }}>
    <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem', color: '#333' }}>{title}</h3>
    <p style={{ color: '#666', marginBottom: '1rem' }}>{description}</p>
    <Link 
      to={link} 
      style={{ 
        color: '#0066cc', 
        textDecoration: 'none', 
        fontWeight: 'bold',
        fontSize: '0.9rem'
      }}
    >
      Learn More →
    </Link>
  </div>
);

// Upload Page with actual file upload functionality
const UploadPage = () => {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  // Get backend URL from environment
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

  const handleFileUpload = async (file) => {
    if (!file) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setUploadStatus({
        type: 'error',
        message: 'Please upload a CSV file only.',
        details: null
      });
      return;
    }

    // Validate file size (20MB limit)
    if (file.size > 20 * 1024 * 1024) {
      setUploadStatus({
        type: 'error',
        message: 'File too large. Please upload files smaller than 20MB.',
        details: null
      });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('account_id', 'default-account');

      console.log('Uploading to:', `${API_BASE_URL}/api/ingest`);

      const response = await axios.post(`${API_BASE_URL}/api/ingest`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const result = response.data;

      if (result.success) {
        setUploadStatus({
          type: 'success',
          message: 'CSV file processed successfully!',
          details: {
            imported: result.imported,
            skipped: result.skipped,
            categorized_pct: result.categorized_pct,
            total_processed: result.total_processed
          }
        });
      } else {
        setUploadStatus({
          type: 'error',
          message: result.error || 'Failed to process CSV file',
          details: result.suggestion ? { suggestion: result.suggestion } : null
        });
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Failed to upload file. Please check the backend connection.',
        details: null
      });
    } finally {
      setIsUploading(false);
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
      <h2 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#333' }}>📁 CSV Upload</h2>
      
      {/* Upload Area */}
      <div 
        style={{ 
          border: dragActive ? '2px solid #0066cc' : '2px dashed #ddd', 
          borderRadius: '8px', 
          padding: '3rem', 
          textAlign: 'center',
          backgroundColor: dragActive ? '#f0f8ff' : '#f9f9f9',
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        
        <p style={{ fontSize: '1.2rem', color: '#666', marginBottom: '1rem' }}>
          {dragActive ? 'Drop your CSV file here' : 'Upload your transaction CSV files here'}
        </p>
        <p style={{ color: '#888', marginBottom: '2rem' }}>
          BannkMint AI will automatically categorize and deduplicate your transactions
        </p>
        
        <button 
          style={{ 
            backgroundColor: isUploading ? '#ccc' : '#0066cc', 
            color: 'white', 
            border: 'none', 
            padding: '0.75rem 1.5rem', 
            borderRadius: '4px',
            fontSize: '1rem',
            cursor: isUploading ? 'not-allowed' : 'pointer'
          }}
          disabled={isUploading}
        >
          {isUploading ? 'Processing...' : 'Choose CSV File'}
        </button>
        
        <p style={{ fontSize: '0.8rem', color: '#999', marginTop: '1rem' }}>
          Supports .csv files up to 20MB. Drag and drop or click to browse.
        </p>
      </div>

      {/* Upload Status */}
      {uploadStatus && (
        <div 
          style={{ 
            marginTop: '2rem',
            padding: '1rem',
            borderRadius: '4px',
            backgroundColor: uploadStatus.type === 'success' ? '#d4edda' : '#f8d7da',
            border: `1px solid ${uploadStatus.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`,
            color: uploadStatus.type === 'success' ? '#155724' : '#721c24'
          }}
        >
          <h4 style={{ margin: '0 0 0.5rem 0' }}>
            {uploadStatus.type === 'success' ? '✅ Success!' : '❌ Error'}
          </h4>
          <p style={{ margin: '0 0 1rem 0' }}>{uploadStatus.message}</p>
          
          {uploadStatus.details && uploadStatus.type === 'success' && (
            <div style={{ fontSize: '0.9rem' }}>
              <p><strong>Imported:</strong> {uploadStatus.details.imported} transactions</p>
              {uploadStatus.details.skipped > 0 && (
                <p><strong>Skipped (duplicates):</strong> {uploadStatus.details.skipped}</p>
              )}
              <p><strong>Auto-categorized:</strong> {uploadStatus.details.categorized_pct}%</p>
              <p><strong>Total processed:</strong> {uploadStatus.details.total_processed} rows</p>
            </div>
          )}
          
          {uploadStatus.details?.suggestion && (
            <p style={{ fontSize: '0.9rem', fontStyle: 'italic' }}>
              💡 {uploadStatus.details.suggestion}
            </p>
          )}
          
          {uploadStatus.type === 'success' && (
            <div style={{ marginTop: '1rem' }}>
              <Link 
                to="/reconcile"
                style={{
                  backgroundColor: '#28a745',
                  color: 'white',
                  padding: '0.5rem 1rem',
                  textDecoration: 'none',
                  borderRadius: '4px',
                  marginRight: '1rem',
                  display: 'inline-block'
                }}
              >
                Review Transactions →
              </Link>
              <Link 
                to="/forecast"
                style={{
                  backgroundColor: '#17a2b8',
                  color: 'white',
                  padding: '0.5rem 1rem',
                  textDecoration: 'none',
                  borderRadius: '4px',
                  display: 'inline-block'
                }}
              >
                View Forecast →
              </Link>
            </div>
          )}
        </div>
      )}
      
      {/* Instructions */}
      <div style={{ marginTop: '2rem', fontSize: '0.9rem', color: '#666' }}>
        <h4>Supported CSV Format:</h4>
        <ul>
          <li>Required columns: date, description, amount (or debit/credit)</li>
          <li>Optional columns: balance, category</li>
          <li>Date formats: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, and more</li>
          <li>Amount formats: $1,234.56, (1234.56), 1234.56</li>
        </ul>
      </div>
    </div>
  );
};

// Reconcile Page with REAL API data
const ReconcilePage = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/reconcile/inbox`);
        setTransactions(response.data.transactions || []);
      } catch (error) {
        console.error('Error fetching transactions:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, []);

  if (loading) {
    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '2rem', color: '#333' }}>🔄 AI Reconciliation</h2>
        <p>Loading transactions...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
      <h2 style={{ fontSize: '2rem', marginBottom: '2rem', color: '#333' }}>🔄 AI Reconciliation</h2>
      <div style={{ 
        border: '1px solid #ddd', 
        borderRadius: '8px', 
        padding: '2rem',
        backgroundColor: 'white'
      }}>
        <h3 style={{ marginBottom: '1rem' }}>Transaction Review ({transactions.length} transactions)</h3>
        <p style={{ color: '#666', marginBottom: '2rem' }}>
          Review AI-categorized transactions with confidence scores and explanations.
        </p>
        
        {transactions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
            <p>No transactions found. Upload a CSV file to get started.</p>
            <Link to="/upload" style={{ color: '#0066cc', textDecoration: 'none', fontWeight: 'bold' }}>
              Upload CSV File →
            </Link>
          </div>
        ) : (
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {transactions.slice(0, 20).map((transaction, index) => (
              <div key={transaction.id || index} style={{ 
                backgroundColor: '#f8f9fa', 
                padding: '1rem', 
                borderRadius: '4px',
                marginBottom: '1rem',
                border: '1px solid #e9ecef'
              }}>
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: '1rem', alignItems: 'center' }}>
                  <div>
                    <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>{transaction.description}</h4>
                    <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>
                      {transaction.posted_at ? new Date(transaction.posted_at).toLocaleDateString() : 'No date'}
                    </p>
                  </div>
                  <div>
                    <strong style={{ color: transaction.amount < 0 ? '#dc3545' : '#28a745' }}>
                      ${Math.abs(transaction.amount).toFixed(2)}
                    </strong>
                  </div>
                  <div>
                    <span style={{
                      backgroundColor: '#e3f2fd',
                      color: '#1976d2',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '12px',
                      fontSize: '0.8rem'
                    }}>
                      {transaction.category}
                    </span>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: '#666' }}>
                      {Math.round((transaction.confidence || 0) * 100)}% confidence
                    </span>
                  </div>
                </div>
                {transaction.why && (
                  <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.8rem', color: '#666', fontStyle: 'italic' }}>
                    {transaction.why}
                  </p>
                )}
              </div>
            ))}
            {transactions.length > 20 && (
              <p style={{ textAlign: 'center', color: '#666', marginTop: '1rem' }}>
                Showing first 20 of {transactions.length} transactions
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Forecast Page
const ForecastPage = () => (
  <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
    <h2 style={{ fontSize: '2rem', marginBottom: '2rem', color: '#333' }}>📊 Cash Flow Forecast</h2>
    <div style={{ 
      border: '1px solid #ddd', 
      borderRadius: '8px', 
      padding: '2rem',
      backgroundColor: 'white'
    }}>
      <h3 style={{ marginBottom: '1rem' }}>8-Week SMB Forecast</h3>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        AI-powered cash flow forecasting with crisis prevention alerts.
      </p>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div style={{ backgroundColor: '#e8f5e8', padding: '1rem', borderRadius: '4px' }}>
          <h4>Current Balance</h4>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#2d5a2d' }}>$25,000</p>
        </div>
        <div style={{ backgroundColor: '#e8f4fd', padding: '1rem', borderRadius: '4px' }}>
          <h4>8-Week Projection</h4>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1e5a8a' }}>$32,500</p>
        </div>
        <div style={{ backgroundColor: '#fff3cd', padding: '1rem', borderRadius: '4px' }}>
          <h4>Confidence</h4>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#856404' }}>78%</p>
        </div>
      </div>
    </div>
  </div>
);

// Main App Component
function App() {
  return (
    <Router>
      <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
        <Navigation />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/reconcile" element={<ReconcilePage />} />
          <Route path="/forecast" element={<ForecastPage />} />
        </Routes>
        
        <footer style={{ 
          textAlign: 'center', 
          padding: '2rem', 
          marginTop: '4rem', 
          borderTop: '1px solid #ddd',
          backgroundColor: 'white'
        }}>
          <p style={{ color: '#666' }}>
            <strong>BannkMint AI SMB Banking OS v0.2.0</strong> - Empowering SMB Financial Intelligence
          </p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
