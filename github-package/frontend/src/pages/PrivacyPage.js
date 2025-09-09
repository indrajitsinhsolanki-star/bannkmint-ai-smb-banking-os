import React from 'react';

const PrivacyPage = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="prose max-w-none">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <p className="text-blue-800">
            <strong>Last updated:</strong> September 2025
          </p>
          <p className="text-blue-800 mt-2">
            BannkMint AI is committed to protecting your privacy and financial data with bank-grade security.
          </p>
        </div>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Information We Collect</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Financial Data</h3>
              <p className="text-gray-600">
                We collect transaction data you upload to provide categorization and forecasting services. 
                This includes transaction dates, descriptions, amounts, and account balances.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Usage Information</h3>
              <p className="text-gray-600">
                We collect information about how you use our service to improve functionality and user experience.
              </p>
            </div>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">How We Use Your Information</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-600">
            <li>Provide AI-powered transaction categorization</li>
            <li>Generate cash flow forecasts and business insights</li>
            <li>Improve our machine learning models</li>
            <li>Ensure service security and prevent fraud</li>
            <li>Provide customer support</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Data Security</h2>
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-green-900 mb-2">Bank-Grade Protection</h3>
            <ul className="list-disc list-inside space-y-2 text-green-800">
              <li>AES-256 encryption for data at rest and in transit</li>
              <li>SOC 2 Type II compliance framework</li>
              <li>Regular security audits and penetration testing</li>
              <li>Multi-factor authentication requirements</li>
              <li>Zero-trust network architecture</li>
            </ul>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Data Sharing</h2>
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-red-900 mb-2">We Do NOT Sell Your Data</h3>
            <p className="text-red-800 mb-4">
              BannkMint AI will never sell, rent, or share your financial data with third parties for marketing purposes.
            </p>
            <div>
              <h4 className="font-medium text-red-900 mb-2">Limited Sharing Only For:</h4>
              <ul className="list-disc list-inside space-y-1 text-red-800">
                <li>Legal compliance when required by law</li>
                <li>Service providers under strict confidentiality agreements</li>
                <li>Business transfers (with prior notice to users)</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Your Rights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Data Control</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                <li>Access your data anytime</li>
                <li>Request data corrections</li>
                <li>Export your data (CSV/JSON)</li>
                <li>Delete your account and data</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Privacy Options</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                <li>Opt out of analytics tracking</li>
                <li>Control marketing communications</li>
                <li>Manage data retention periods</li>
                <li>Request data portability</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">GDPR & CCPA Compliance</h2>
          <p className="text-gray-600 mb-4">
            BannkMint AI complies with international privacy regulations including GDPR and CCPA. 
            Users have the right to:
          </p>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <ul className="list-disc list-inside space-y-1 text-gray-700">
              <li>Know what personal information is collected and how it's used</li>
              <li>Request deletion of personal information</li>
              <li>Opt-out of the sale of personal information (we don't sell data)</li>
              <li>Non-discrimination for exercising privacy rights</li>
            </ul>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Contact Us</h2>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <p className="text-gray-700 mb-4">
              Questions about our privacy practices? We're here to help.
            </p>
            <div className="space-y-2 text-gray-700">
              <p><strong>Email:</strong> privacy@bannkmint.ai</p>
              <p><strong>Address:</strong> BannkMint AI Privacy Team, 123 Financial District, San Francisco, CA 94105</p>
              <p><strong>Response Time:</strong> We respond to privacy requests within 48 hours</p>
            </div>
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Updates to This Policy</h2>
          <p className="text-gray-600">
            We may update this privacy policy as our service evolves. We'll notify users of any material 
            changes via email and update the "Last updated" date at the top of this policy.
          </p>
        </section>
      </div>
    </div>
  );
};

export default PrivacyPage;