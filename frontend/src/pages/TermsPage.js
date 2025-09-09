import React from 'react';

const TermsPage = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Terms of Service</h1>
      
      <div className="bg-white rounded-lg shadow-md p-8 space-y-6">
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Service Description</h2>
          <p className="text-gray-600">
            BannkMint AI is a financial intelligence platform that provides automated transaction 
            categorization, reconciliation tools, and cash flow forecasting capabilities.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Acceptable Use</h2>
          <p className="text-gray-600">
            You agree to use BannkMint AI only for legitimate business and personal financial 
            management purposes. You will not:
          </p>
          <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
            <li>Upload fraudulent or illegal transaction data</li>
            <li>Attempt to reverse engineer our AI algorithms</li>
            <li>Use the service to harm others or violate laws</li>
            <li>Share your account credentials with unauthorized parties</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Data Accuracy</h2>
          <p className="text-gray-600">
            While BannkMint AI uses advanced AI to categorize transactions, we cannot guarantee 
            100% accuracy. You are responsible for reviewing and validating all categorizations 
            before making financial decisions.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Limitation of Liability</h2>
          <p className="text-gray-600">
            BannkMint AI is provided "as is" without warranties. We are not liable for any 
            financial decisions made based on our analysis or for any data loss or security breaches.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Service Availability</h2>
          <p className="text-gray-600">
            We strive to maintain high service availability but cannot guarantee uninterrupted 
            access. We may perform maintenance or updates that temporarily affect service availability.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Changes to Terms</h2>
          <p className="text-gray-600">
            We may update these terms from time to time. Continued use of the service after 
            changes constitutes acceptance of the new terms.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Contact Information</h2>
          <p className="text-gray-600">
            For questions about these terms, please contact us at legal@bankmint.ai
          </p>
        </section>
      </div>
    </div>
  );
};

export default TermsPage;