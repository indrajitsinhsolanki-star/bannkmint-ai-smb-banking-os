import React from 'react';

const PrivacyPage = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
      
      <div className="bg-white rounded-lg shadow-md p-8 space-y-6">
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Data Collection</h2>
          <p className="text-gray-600">
            BannkMint AI processes your financial transaction data locally to provide categorization 
            and analysis services. We collect only the data necessary to deliver our core functionality.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Data Storage</h2>
          <p className="text-gray-600">
            Your transaction data is stored securely in a local SQLite database. We do not 
            transmit your financial data to external servers except where explicitly required 
            for service functionality.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Data Usage</h2>
          <p className="text-gray-600">
            We use your transaction data to:
          </p>
          <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
            <li>Automatically categorize transactions using AI</li>
            <li>Learn from your corrections to improve accuracy</li>
            <li>Generate cash flow forecasts and insights</li>
            <li>Detect patterns and anomalies in your financial data</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Data Security</h2>
          <p className="text-gray-600">
            We implement appropriate technical and organizational measures to protect your 
            data against unauthorized access, alteration, disclosure, or destruction.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Your Rights</h2>
          <p className="text-gray-600">
            You have the right to access, correct, or delete your data at any time. 
            Contact us if you have any questions about your data or this privacy policy.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Contact Information</h2>
          <p className="text-gray-600">
            For privacy-related questions, please contact us at privacy@bankmint.ai
          </p>
        </section>
      </div>
    </div>
  );
};

export default PrivacyPage;