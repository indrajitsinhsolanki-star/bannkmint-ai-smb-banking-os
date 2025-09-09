import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
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

// Upload Page
const UploadPage = () => (
  <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
    <h2 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#333' }}>📁 CSV Upload</h2>
    <div style={{ 
      border: '2px dashed #ddd', 
      borderRadius: '8px', 
      padding: '3rem', 
      textAlign: 'center',
      backgroundColor: '#f9f9f9'
    }}>
      <p style={{ fontSize: '1.2rem', color: '#666', marginBottom: '1rem' }}>
        Upload your transaction CSV files here
      </p>
      <p style={{ color: '#888' }}>
        BannkMint AI will automatically categorize and deduplicate your transactions
      </p>
      <div style={{ marginTop: '2rem' }}>
        <button style={{ 
          backgroundColor: '#0066cc', 
          color: 'white', 
          border: 'none', 
          padding: '0.75rem 1.5rem', 
          borderRadius: '4px',
          fontSize: '1rem',
          cursor: 'pointer'
        }}>
          Choose CSV File
        </button>
      </div>
    </div>
  </div>
);

// Reconcile Page
const ReconcilePage = () => (
  <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
    <h2 style={{ fontSize: '2rem', marginBottom: '2rem', color: '#333' }}>🔄 AI Reconciliation</h2>
    <div style={{ 
      border: '1px solid #ddd', 
      borderRadius: '8px', 
      padding: '2rem',
      backgroundColor: 'white'
    }}>
      <h3 style={{ marginBottom: '1rem' }}>Transaction Review</h3>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        Review AI-categorized transactions with confidence scores and explanations.
      </p>
      
      <div style={{ backgroundColor: '#f8f9fa', padding: '1rem', borderRadius: '4px' }}>
        <h4>Sample Transaction</h4>
        <p><strong>Description:</strong> Coffee Shop Purchase</p>
        <p><strong>Amount:</strong> -$4.50</p>
        <p><strong>Category:</strong> Meals & Entertainment (Confidence: 95%)</p>
        <p><strong>Explanation:</strong> Matched pattern: 'coffee'</p>
      </div>
    </div>
  </div>
);

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
