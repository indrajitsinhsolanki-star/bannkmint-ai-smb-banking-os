import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();
  
  const tabs = [
    { id: 'upload', label: 'Upload', path: '/' },
    { id: 'reconcile', label: 'Reconcile', path: '/reconcile' },
    { id: 'forecast', label: 'Forecast', path: '/forecast' },
    { id: 'privacy', label: 'Privacy', path: '/privacy' },
    { id: 'terms', label: 'Terms', path: '/terms' },
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold text-blue-600">BannkMint AI</h1>
              <p className="text-xs text-gray-500">v0.2 - Financial Intelligence</p>
            </div>
          </div>
          
          {/* Navigation tabs */}
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const isActive = location.pathname === tab.path;
              return (
                <Link
                  key={tab.id}
                  to={tab.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-500'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {tab.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;