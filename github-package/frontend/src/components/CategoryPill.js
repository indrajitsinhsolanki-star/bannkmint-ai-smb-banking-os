import React, { useState } from 'react';

const CategoryPill = ({ 
  category, 
  vendor, 
  isEditable = false, 
  onSave,
  availableCategories = []
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(category || 'Uncategorized');
  const [selectedVendor, setSelectedVendor] = useState(vendor || '');
  
  const defaultCategories = [
    'Software & Technology',
    'Marketing & Advertising', 
    'Payment Processing Fees',
    'Transportation',
    'Meals & Entertainment',
    'Office Supplies',
    'Taxes',
    'Payroll',
    'Utilities',
    'Insurance',
    'Professional Services',
    'Banking Fees',
    'Internal Transfer',
    'Uncategorized'
  ];

  const categories = availableCategories.length > 0 ? availableCategories : defaultCategories;

  const getCategoryColor = (cat) => {
    const colorMap = {
      'Software & Technology': 'bg-blue-100 text-blue-800 border-blue-200',
      'Marketing & Advertising': 'bg-purple-100 text-purple-800 border-purple-200',
      'Payment Processing Fees': 'bg-orange-100 text-orange-800 border-orange-200',
      'Transportation': 'bg-green-100 text-green-800 border-green-200',
      'Meals & Entertainment': 'bg-pink-100 text-pink-800 border-pink-200',
      'Office Supplies': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'Taxes': 'bg-red-100 text-red-800 border-red-200',
      'Payroll': 'bg-indigo-100 text-indigo-800 border-indigo-200',
      'Utilities': 'bg-cyan-100 text-cyan-800 border-cyan-200',
      'Insurance': 'bg-teal-100 text-teal-800 border-teal-200',
      'Professional Services': 'bg-gray-100 text-gray-800 border-gray-200',
      'Banking Fees': 'bg-stone-100 text-stone-800 border-stone-200',
      'Internal Transfer': 'bg-slate-100 text-slate-800 border-slate-200',
      'Uncategorized': 'bg-red-50 text-red-600 border-red-200',
    };
    return colorMap[cat] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const handleSave = () => {
    if (onSave) {
      onSave({
        category: selectedCategory,
        vendor: selectedVendor
      });
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setSelectedCategory(category || 'Uncategorized');
    setSelectedVendor(vendor || '');
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="flex flex-col space-y-2 min-w-64">
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="block w-full px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
        
        <input
          type="text"
          value={selectedVendor}
          onChange={(e) => setSelectedVendor(e.target.value)}
          placeholder="Vendor name (optional)"
          className="block w-full px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        
        <div className="flex space-x-2">
          <button
            onClick={handleSave}
            className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Save
          </button>
          <button
            onClick={handleCancel}
            className="px-3 py-1 bg-gray-300 text-gray-700 text-xs rounded hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-1">
      <span 
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getCategoryColor(category)} ${isEditable ? 'cursor-pointer hover:opacity-80' : ''}`}
        onClick={isEditable ? () => setIsEditing(true) : undefined}
        title={isEditable ? 'Click to edit category' : ''}
      >
        {category || 'Uncategorized'}
        {isEditable && (
          <svg className="ml-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
        )}
      </span>
      {vendor && (
        <span className="text-xs text-gray-500">
          {vendor}
        </span>
      )}
    </div>
  );
};

export default CategoryPill;