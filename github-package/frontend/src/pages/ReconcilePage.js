import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import ConfidenceBadge from '../components/ConfidenceBadge';
import CategoryPill from '../components/CategoryPill';

const ReconcilePage = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTransactions, setSelectedTransactions] = useState(new Set());
  const [minConfidence, setMinConfidence] = useState(0.9);
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 });
  const [showRulesPanel, setShowRulesPanel] = useState(false);
  const [rules, setRules] = useState([]);

  useEffect(() => {
    loadTransactions();
    loadRules();
  }, [minConfidence, pagination.page]);

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const response = await api.getReconciliationInbox(minConfidence, pagination.page);
      setTransactions(response.data.transactions);
      setPagination({
        page: response.data.page,
        pages: response.data.pages,
        total: response.data.total
      });
      setError(null);
    } catch (err) {
      setError('Failed to load transactions');
      console.error('Error loading transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRules = async () => {
    try {
      const response = await api.getRules();
      setRules(response.data);
    } catch (err) {
      console.error('Error loading rules:', err);
    }
  };

  const handleCategorizeTransaction = async (transactionId, categoryData, makeRule = false, pattern = '') => {
    try {
      const payload = {
        category: categoryData.category,
        vendor: categoryData.vendor,
        make_rule: makeRule,
        pattern: pattern
      };

      await api.categorizeTransaction(transactionId, payload);
      
      // Reload transactions and rules
      await loadTransactions();
      if (makeRule) {
        await loadRules();
      }
      
      // Show success message
      setError(null);
    } catch (err) {
      setError('Failed to categorize transaction');
      console.error('Error categorizing transaction:', err);
    }
  };

  const handleBulkAccept = async () => {
    if (selectedTransactions.size === 0) return;

    try {
      // Accept all selected transactions by marking them as reviewed
      const promises = Array.from(selectedTransactions).map(transactionId => {
        const transaction = transactions.find(t => t.id === transactionId);
        if (transaction && transaction.confidence >= 0.85) {
          return api.categorizeTransaction(transactionId, {
            category: transaction.category,
            vendor: transaction.vendor,
            make_rule: false
          });
        }
        return Promise.resolve();
      });

      await Promise.all(promises);
      setSelectedTransactions(new Set());
      await loadTransactions();
    } catch (err) {
      setError('Failed to accept transactions');
      console.error('Error accepting transactions:', err);
    }
  };

  const toggleTransactionSelection = (transactionId) => {
    const newSelected = new Set(selectedTransactions);
    if (newSelected.has(transactionId)) {
      newSelected.delete(transactionId);
    } else {
      newSelected.add(transactionId);
    }
    setSelectedTransactions(newSelected);
  };

  const formatAmount = (amount) => {
    const abs = Math.abs(amount);
    const formatted = abs.toLocaleString('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 2 
    });
    return amount < 0 ? `-${formatted}` : formatted;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
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
            <span className="text-lg text-gray-600">Loading transactions...</span>
          </div>
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
            Reconciliation Inbox
          </h1>
          <p className="text-lg text-gray-600">
            Review and categorize {pagination.total} transactions needing attention
          </p>
        </div>
        <button
          onClick={() => setShowRulesPanel(!showRulesPanel)}
          className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          {showRulesPanel ? 'Hide Rules' : 'Manage Rules'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">
              Show transactions with confidence below:
            </label>
            <select
              value={minConfidence}
              onChange={(e) => {
                setMinConfidence(parseFloat(e.target.value));
                setPagination(prev => ({ ...prev, page: 1 }));
              }}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={1.0}>100% (Show all)</option>
              <option value={0.95}>95%</option>
              <option value={0.9}>90%</option>
              <option value={0.85}>85%</option>
              <option value={0.8}>80%</option>
              <option value={0.75}>75%</option>
            </select>
          </div>
          
          {selectedTransactions.size > 0 && (
            <button
              onClick={handleBulkAccept}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              Accept {selectedTransactions.size} Selected
            </button>
          )}
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    checked={selectedTransactions.size === transactions.length && transactions.length > 0}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedTransactions(new Set(transactions.map(t => t.id)));
                      } else {
                        setSelectedTransactions(new Set());
                      }
                    }}
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {transactions.map((transaction) => (
                <tr key={transaction.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedTransactions.has(transaction.id)}
                      onChange={() => toggleTransactionSelection(transaction.id)}
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(transaction.posted_at)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {transaction.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                    <span className={transaction.amount < 0 ? 'text-red-600' : 'text-green-600'}>
                      {formatAmount(transaction.amount)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <CategoryPill
                      category={transaction.category}
                      vendor={transaction.vendor}
                      isEditable={true}
                      onSave={(data) => handleCategorizeTransaction(transaction.id, data)}
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <ConfidenceBadge 
                      confidence={transaction.confidence} 
                      why={transaction.why}
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          const pattern = prompt('Enter pattern for rule (e.g., vendor name):');
                          if (pattern) {
                            handleCategorizeTransaction(
                              transaction.id, 
                              { category: transaction.category, vendor: transaction.vendor },
                              true,
                              pattern
                            );
                          }
                        }}
                        className="text-blue-600 hover:text-blue-800 text-xs"
                        title="Create rule from this transaction"
                      >
                        Make Rule
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {transactions.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">All transactions reviewed!</h3>
            <p className="mt-1 text-gray-500">
              No transactions need review at the current confidence threshold.
            </p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {pagination.pages > 1 && (
        <div className="flex justify-between items-center mt-6">
          <p className="text-sm text-gray-600">
            Showing page {pagination.page} of {pagination.pages} ({pagination.total} total)
          </p>
          <div className="flex space-x-2">
            <button
              onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
              disabled={pagination.page <= 1}
              className="px-3 py-1 bg-gray-300 text-gray-700 rounded disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
              disabled={pagination.page >= pagination.pages}
              className="px-3 py-1 bg-gray-300 text-gray-700 rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Rules Panel */}
      {showRulesPanel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full m-4 max-h-[80vh] overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Categorization Rules</h2>
              <button
                onClick={() => setShowRulesPanel(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-6 overflow-y-auto">
              <div className="space-y-4">
                {rules.map((rule) => (
                  <div key={rule.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <span className="text-sm font-medium text-gray-900">
                          {rule.match_type}: "{rule.pattern}"
                        </span>
                        <span className="text-sm text-gray-500">→</span>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {rule.set_category}
                        </span>
                      </div>
                      <div className="mt-1 text-xs text-gray-500">
                        Priority: {rule.priority} | Used: {rule.hits} times
                      </div>
                    </div>
                    <button
                      onClick={async () => {
                        if (confirm('Delete this rule?')) {
                          try {
                            await api.deleteRule(rule.id);
                            await loadRules();
                          } catch (err) {
                            setError('Failed to delete rule');
                          }
                        }
                      }}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReconcilePage;