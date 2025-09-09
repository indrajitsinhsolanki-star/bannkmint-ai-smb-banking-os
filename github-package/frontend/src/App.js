import React, { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { api } from './services/api';

// Components
import Navigation from './components/Navigation';

// Pages
import UploadPage from './pages/UploadPage';
import ReconcilePage from './pages/ReconcilePage';
import ForecastPage from './pages/ForecastPage';
import PrivacyPage from './pages/PrivacyPage';
import TermsPage from './pages/TermsPage';

function App() {
  // Health check on app load
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await api.health();
        console.log('BannkMint AI Backend Status:', response.data);
      } catch (error) {
        console.error('Backend health check failed:', error);
      }
    };

    checkHealth();
  }, []);

  return (
    <div className="App min-h-screen bg-gray-50">
      <BrowserRouter>
        <Navigation />
        <main>
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/reconcile" element={<ReconcilePage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/privacy" element={<PrivacyPage />} />
            <Route path="/terms" element={<TermsPage />} />
          </Routes>
        </main>
      </BrowserRouter>
    </div>
  );
}

export default App;