import React from 'react';

const ConfidenceBadge = ({ confidence, why }) => {
  const getConfidenceColor = (conf) => {
    if (conf >= 0.95) return 'bg-green-100 text-green-800 border-green-200';
    if (conf >= 0.85) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (conf >= 0.75) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  const getConfidenceLabel = (conf) => {
    if (conf >= 0.95) return 'High';
    if (conf >= 0.85) return 'Good';
    if (conf >= 0.75) return 'Medium';
    return 'Low';
  };

  const formatWhy = (why) => {
    if (!why) return 'No explanation';
    
    if (why.startsWith('rule:')) {
      return `Rule: "${why.substring(5)}"`;
    }
    if (why.startsWith('heuristic:')) {
      return `Keyword: "${why.substring(10)}"`;
    }
    if (why.startsWith('memory:')) {
      return `Learned: ${why.substring(7)}`;
    }
    if (why === 'user_correction') {
      return 'User corrected';
    }
    if (why === 'none') {
      return 'No pattern matched';
    }
    
    return why;
  };

  if (!confidence && confidence !== 0) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
        Unknown
      </span>
    );
  }

  return (
    <div className="flex items-center space-x-2">
      <span 
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getConfidenceColor(confidence)}`}
        title={formatWhy(why)}
      >
        {getConfidenceLabel(confidence)} ({Math.round(confidence * 100)}%)
      </span>
      {why && (
        <span className="text-xs text-gray-500 italic" title={formatWhy(why)}>
          {formatWhy(why)}
        </span>
      )}
    </div>
  );
};

export default ConfidenceBadge;