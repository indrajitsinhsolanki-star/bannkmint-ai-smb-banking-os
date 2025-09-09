import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
const API_URL = `${API_BASE}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const api = {
  // Health check
  health: () => apiClient.get('/health'),

  // CSV ingestion
  uploadCSV: (file, accountId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (accountId) {
      formData.append('account_id', accountId);
    }
    
    return apiClient.post('/ingest', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Reconciliation
  getReconciliationInbox: (minConf = 0.9, page = 1, limit = 50) => 
    apiClient.get(`/reconcile/inbox?min_conf=${minConf}&page=${page}&limit=${limit}`),

  categorizeTransaction: (transactionId, data) =>
    apiClient.post(`/transactions/${transactionId}/categorize`, data),

  // Rules management
  getRules: () => apiClient.get('/rules'),
  
  createRule: (rule) => apiClient.post('/rules', rule),
  
  deleteRule: (ruleId) => apiClient.delete(`/rules/${ruleId}`),

  // SMB-Focused Forecast endpoints (Phase 3B)
  getForecast: (weeks = 6, scenario = 'base', accountId = null) => {
    const params = new URLSearchParams();
    params.append('weeks', Math.max(4, Math.min(weeks, 8))); // Force 4-8 weeks
    params.append('scenario', scenario);
    if (accountId) {
      params.append('account_id', accountId);
    }
    return apiClient.get(`/forecast?${params.toString()}`);
  },

  getCrisisAnalysis: (weeks = 6, accountId = null) => {
    const params = new URLSearchParams();
    params.append('weeks', weeks);
    if (accountId) {
      params.append('account_id', accountId);
    }
    return apiClient.get(`/forecast/crisis-analysis?${params.toString()}`);
  },

  getScenarioPlanning: (weeks = 6, accountId = null) => {
    const params = new URLSearchParams();
    params.append('weeks', weeks);
    if (accountId) {
      params.append('account_id', accountId);
    }
    return apiClient.get(`/forecast/scenario-planning?${params.toString()}`);
  },

  getRecurringPatterns: (accountId = null) => {
    const params = new URLSearchParams();
    if (accountId) {
      params.append('account_id', accountId);
    }
    return apiClient.get(`/forecast/patterns?${params.toString()}`);
  },

  // Banking Integration endpoints (Phase 3A)
  getSupportedBanks: () => apiClient.get('/banking/institutions'),
  
  connectBank: (bankId, businessName = 'My Business') => 
    apiClient.post(`/banking/connect?bank_id=${bankId}&business_name=${encodeURIComponent(businessName)}`),
  
  getBankConnections: () => apiClient.get('/banking/connections'),
  
  getFinancialOverview: () => apiClient.get('/banking/overview'),

  // Month-End Reporting endpoints
  getMonthEndPack: (month = null, year = null, accountIds = null) => {
    const params = new URLSearchParams();
    if (month) params.append('month', month);
    if (year) params.append('year', year);
    if (accountIds) params.append('account_ids', accountIds);
    return apiClient.get(`/reports/month-end?${params.toString()}`);
  },

  getProfitLossReport: (month = null, year = null, accountIds = null) => {
    const params = new URLSearchParams();
    if (month) params.append('month', month);
    if (year) params.append('year', year);
    if (accountIds) params.append('account_ids', accountIds);
    return apiClient.get(`/reports/profit-loss?${params.toString()}`);
  },

  // Legacy endpoints
  categorizeTransactions: (data) => apiClient.post('/categorize-transactions', data),
  cleanCSV: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/clean-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export default api;