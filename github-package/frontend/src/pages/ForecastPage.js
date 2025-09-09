import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { api } from '../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const ForecastPage = () => {
  const [forecastData, setForecastData] = useState(null);
  const [crisisAnalysis, setCrisisAnalysis] = useState(null);
  const [scenarioData, setScenarioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedWeeks, setSelectedWeeks] = useState(6);
  const [selectedScenario, setSelectedScenario] = useState('base');

  useEffect(() => {
    loadAllForecastData();
  }, [selectedWeeks, selectedScenario]);

  const loadAllForecastData = async () => {
    setLoading(true);
    try {
      const [forecastResponse, crisisResponse, scenarioResponse] = await Promise.all([
        api.getForecast(selectedWeeks, selectedScenario),
        api.getCrisisAnalysis(selectedWeeks),
        api.getScenarioPlanning(selectedWeeks)
      ]);
      
      setForecastData(forecastResponse.data);
      setCrisisAnalysis(crisisResponse.data);
      setScenarioData(scenarioResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to load forecast data');
      console.error('Forecast error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const getCashFlowChartData = () => {
    if (!forecastData?.daily_projections) return null;

    const projections = forecastData.daily_projections;
    const crisisThreshold = forecastData.crisis_threshold || 10000;
    
    return {
      labels: projections.map(p => formatDate(p.date)),
      datasets: [
        {
          label: 'Projected Cash Balance',
          data: projections.map(p => p.cash_balance),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.1,
        },
        {
          label: 'Crisis Threshold ($10K)',
          data: projections.map(() => crisisThreshold),
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0,
        }
      ]
    };
  };

  const getScenarioComparisonData = () => {
    if (!scenarioData?.scenarios) return null;

    const scenarios = scenarioData.scenarios;
    const scenarioNames = ['pessimistic', 'base', 'optimistic'];
    
    return {
      labels: scenarioNames.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
      datasets: [
        {
          label: 'Ending Cash Balance',
          data: scenarioNames.map(s => scenarios[s]?.ending_cash || 0),
          backgroundColor: [
            'rgba(239, 68, 68, 0.8)',   // Red for pessimistic
            'rgba(59, 130, 246, 0.8)',  // Blue for base
            'rgba(34, 197, 94, 0.8)'    // Green for optimistic
          ],
          borderColor: [
            'rgb(239, 68, 68)',
            'rgb(59, 130, 246)', 
            'rgb(34, 197, 94)'
          ],
          borderWidth: 2,
        }
      ]
    };
  };

  const getAlertIcon = (severity) => {
    const icons = {
      critical: '🚨',
      high: '⚠️',
      medium: '💡',
      low: '📊'
    };
    return icons[severity] || '📊';
  };

  const getAlertColor = (severity) => {
    const colors = {
      critical: 'bg-red-50 border-red-200 text-red-800',
      high: 'bg-orange-50 border-orange-200 text-orange-800',
      medium: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      low: 'bg-blue-50 border-blue-200 text-blue-800'
    };
    return colors[severity] || 'bg-gray-50 border-gray-200 text-gray-800';
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'SMB Cash Flow Forecast (4-8 Weeks)'
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || '';
            const value = formatCurrency(context.parsed.y);
            return `${label}: ${value}`;
          }
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value) => formatCurrency(value)
        }
      }
    }
  };

  const scenarioChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: 'Scenario Planning Analysis'
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = formatCurrency(context.parsed.y);
            return `Ending Balance: ${value}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value) => formatCurrency(value)
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2">
            <svg className="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="text-lg text-gray-600">Generating SMB forecast...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <svg className="h-6 w-6 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-medium text-red-900">Forecast Error</h3>
          </div>
          <p className="text-red-700 mt-2">{error}</p>
          <button
            onClick={loadAllForecastData}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            💰 SMB Cash Flow Forecast
          </h1>
          <p className="text-lg text-gray-600">
            Actionable {selectedWeeks}-week projections with crisis prevention
          </p>
          {crisisAnalysis?.cash_runway_days && (
            <p className="text-sm text-gray-500 mt-1">
              Cash Runway: {crisisAnalysis.cash_runway_days} days ({Math.round(crisisAnalysis.cash_runway_days / 7)} weeks)
            </p>
          )}
        </div>
        
        <div className="flex items-center space-x-4">
          <select
            value={selectedWeeks}
            onChange={(e) => setSelectedWeeks(parseInt(e.target.value))}
            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={4}>4 weeks</option>
            <option value={6}>6 weeks</option>
            <option value={8}>8 weeks</option>
          </select>
          
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="pessimistic">Pessimistic</option>
            <option value="base">Base Case</option>
            <option value="optimistic">Optimistic</option>
          </select>
          
          <button
            onClick={loadAllForecastData}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Crisis Alerts */}
      {forecastData?.crisis_alerts && forecastData.crisis_alerts.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🚨 Cash Flow Crisis Alerts</h2>
          <div className="grid grid-cols-1 gap-4">
            {forecastData.crisis_alerts.map((alert, index) => (
              <div key={index} className={`border rounded-lg p-4 ${getAlertColor(alert.severity)}`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-center mb-2">
                    <span className="text-xl mr-2">{getAlertIcon(alert.severity)}</span>
                    <h3 className="font-medium text-lg">{alert.title}</h3>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                    alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {alert.severity.toUpperCase()}
                  </span>
                </div>
                <p className="font-medium text-lg mb-2">{alert.message}</p>
                {alert.projected_balance && (
                  <p className="text-sm mb-3">
                    Projected balance: <span className="font-medium">{formatCurrency(alert.projected_balance)}</span>
                    {alert.date && (
                      <span className="ml-2">on {formatDate(alert.date)}</span>
                    )}
                  </p>
                )}
                {alert.recommendations && (
                  <div className="mt-3">
                    <p className="text-sm font-medium mb-1">Recommended Actions:</p>
                    <ul className="text-sm space-y-1">
                      {alert.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-gray-400 mr-2">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Current Cash</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(forecastData?.current_cash || 0)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Crisis Threshold</p>
              <p className="text-2xl font-bold text-red-600">{formatCurrency(forecastData?.crisis_threshold || 10000)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Cash Runway</p>
              <p className="text-2xl font-bold text-green-600">
                {crisisAnalysis?.cash_runway_days ? `${Math.round(crisisAnalysis.cash_runway_days / 7)}w` : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Patterns Found</p>
              <p className="text-2xl font-bold text-purple-600">{forecastData?.smb_patterns?.length || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Cash Flow Projection Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Cash Balance Projection</h2>
            <span className="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded">
              {selectedScenario.charAt(0).toUpperCase() + selectedScenario.slice(1)} Scenario
            </span>
          </div>
          {getCashFlowChartData() && (
            <Line data={getCashFlowChartData()} options={chartOptions} />
          )}
        </div>

        {/* Scenario Comparison Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Scenario Comparison</h2>
          {getScenarioComparisonData() && (
            <Bar data={getScenarioComparisonData()} options={scenarioChartOptions} />
          )}
          
          {scenarioData?.scenarios && (
            <div className="mt-4 grid grid-cols-3 gap-4 text-center">
              {Object.entries(scenarioData.scenarios).map(([scenario, data]) => (
                <div key={scenario} className="text-sm">
                  <p className="font-medium capitalize">{scenario}</p>
                  <p className={`text-xs ${data.cash_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {data.cash_change >= 0 ? '+' : ''}{formatCurrency(data.cash_change)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* SMB Patterns and Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Critical Business Patterns */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            🏢 Critical Business Patterns
          </h2>
          {forecastData?.smb_patterns && forecastData.smb_patterns.length > 0 ? (
            <div className="space-y-3">
              {forecastData.smb_patterns.slice(0, 8).map((pattern, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{pattern.vendor.replace(/_/g, ' ')}</p>
                      <p className="text-sm text-gray-600">{pattern.category}</p>
                      <p className="text-xs text-gray-500">
                        {pattern.frequency} • Next: {formatDate(pattern.next_expected)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className={`font-medium ${pattern.avg_amount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatCurrency(pattern.avg_amount)}
                      </p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="inline-flex px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                          {Math.round(pattern.confidence * 100)}% sure
                        </span>
                        <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                          pattern.business_criticality > 0.8 ? 'bg-red-100 text-red-800' :
                          pattern.business_criticality > 0.6 ? 'bg-orange-100 text-orange-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {pattern.business_criticality > 0.8 ? 'Critical' :
                           pattern.business_criticality > 0.6 ? 'Important' : 'Normal'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <h3 className="mt-2 text-lg font-medium text-gray-900">No Patterns Detected</h3>
              <p className="mt-1 text-gray-500">Upload more transaction data to detect business patterns</p>
            </div>
          )}
        </div>

        {/* Business Recommendations */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            💡 Business Recommendations
          </h2>
          {forecastData?.recommendations && forecastData.recommendations.length > 0 ? (
            <div className="space-y-4">
              {forecastData.recommendations.map((rec, index) => (
                <div key={index} className="p-4 border rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium text-gray-900">{rec.title}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                      rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {rec.priority.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{rec.category}</p>
                  <ul className="text-sm space-y-1">
                    {rec.actions.map((action, actionIndex) => (
                      <li key={actionIndex} className="flex items-start">
                        <span className="text-gray-400 mr-2">•</span>
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <h3 className="mt-2 text-lg font-medium text-gray-900">All Clear!</h3>
              <p className="mt-1 text-gray-500">No immediate action items detected</p>
            </div>
          )}
        </div>
      </div>

      {/* Business Metrics Footer */}
      {crisisAnalysis?.business_metrics && (
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Business Metrics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-600">Monthly Recurring Revenue</p>
              <p className="font-medium text-green-600">
                {formatCurrency(crisisAnalysis.business_metrics.monthly_recurring_revenue || 0)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Monthly Recurring Expenses</p>
              <p className="font-medium text-red-600">
                {formatCurrency(crisisAnalysis.business_metrics.monthly_recurring_expenses || 0)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Net Monthly Recurring</p>
              <p className={`font-medium ${(crisisAnalysis.business_metrics.net_monthly_recurring || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(crisisAnalysis.business_metrics.net_monthly_recurring || 0)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Forecast Confidence</p>
              <p className="font-medium text-blue-600">
                {Math.round((crisisAnalysis.business_metrics.forecast_confidence || 0) * 100)}%
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ForecastPage;