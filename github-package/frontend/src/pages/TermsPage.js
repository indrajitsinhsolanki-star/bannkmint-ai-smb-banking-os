import React from 'react';

const TermsPage = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="prose max-w-none">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Terms of Service</h1>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <p className="text-blue-800">
            <strong>Last updated:</strong> September 2025
          </p>
          <p className="text-blue-800 mt-2">
            Welcome to BannkMint AI SMB Banking OS. By using our service, you agree to these terms.
          </p>
        </div>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Service Description</h2>
          <p className="text-gray-600 mb-4">
            BannkMint AI provides AI-powered financial intelligence for small and medium businesses, including:
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-600">
            <li>Automated transaction categorization with 95% accuracy</li>
            <li>SMB-focused cash flow forecasting (4-8 week projections)</li>
            <li>Crisis prevention alerts and business recommendations</li>
            <li>Professional month-end reporting packages</li>
            <li>Banking integration foundations for multi-account management</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. User Responsibilities</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Data Accuracy</h3>
              <p className="text-gray-600">
                You are responsible for ensuring the accuracy of financial data you upload. 
                BannkMint AI provides analysis based on the data you provide.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Account Security</h3>
              <p className="text-gray-600">
                You must maintain the confidentiality of your account credentials and notify us 
                immediately of any unauthorized access.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Compliance</h3>
              <p className="text-gray-600">
                You must comply with all applicable laws and regulations when using our service, 
                including financial reporting requirements in your jurisdiction.
              </p>
            </div>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. Service Availability</h2>
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-green-900 mb-2">Service Level Agreement</h3>
            <ul className="list-disc list-inside space-y-2 text-green-800">
              <li>99.9% uptime target for all core services</li>
              <li>Scheduled maintenance windows announced 48 hours in advance</li>
              <li>Real-time status updates at status.bannkmint.ai</li>
              <li>24/7 monitoring and incident response</li>
            </ul>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Pricing and Billing</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Starter</h3>
              <p className="text-2xl font-bold text-blue-600 mb-2">$99/month</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Single business account</li>
                <li>• AI categorization</li>
                <li>• Basic forecasting</li>
                <li>• Email support</li>
              </ul>
            </div>
            <div className="border border-blue-500 rounded-lg p-4 bg-blue-50">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-medium text-gray-900">Professional</h3>
                <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded">POPULAR</span>
              </div>
              <p className="text-2xl font-bold text-blue-600 mb-2">$199/month</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Multiple business accounts</li>
                <li>• Advanced forecasting</li>
                <li>• Crisis prevention alerts</li>
                <li>• Priority support</li>
              </ul>
            </div>
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Enterprise</h3>
              <p className="text-2xl font-bold text-blue-600 mb-2">$499/month</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Unlimited accounts</li>
                <li>• White-label options</li>
                <li>• Custom integrations</li>
                <li>• Dedicated support</li>
              </ul>
            </div>
          </div>
          <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800">
              <strong>Note:</strong> All plans include a 30-day free trial. Cancel anytime with no penalties.
            </p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Limitation of Liability</h2>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <p className="text-gray-700 mb-4">
              BannkMint AI provides financial analysis tools and recommendations. We are not:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>Certified public accountants or financial advisors</li>
              <li>Responsible for business decisions made based on our analysis</li>
              <li>Liable for any financial losses resulting from service use</li>
              <li>Guaranteeing the accuracy of predictions or forecasts</li>
            </ul>
            <p className="text-gray-700 mt-4">
              <strong>Professional Advice:</strong> Always consult with qualified financial professionals 
              for important business decisions.
            </p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Intellectual Property</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Our IP</h3>
              <p className="text-gray-600">
                BannkMint AI retains all rights to our software, algorithms, and intellectual property. 
                You receive a license to use our service, not ownership of our technology.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Your Data</h3>
              <p className="text-gray-600">
                You retain ownership of all financial data you upload. We only use your data to 
                provide our services and improve our AI models (with anonymization).
              </p>
            </div>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Termination</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">By You</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                <li>Cancel subscription anytime</li>
                <li>30-day data retention after cancellation</li>
                <li>Export all data before termination</li>
                <li>Pro-rated refunds available</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">By BannkMint AI</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                <li>Violation of terms of service</li>
                <li>Fraudulent or abusive behavior</li>
                <li>Non-payment of fees</li>
                <li>30-day notice for non-violation terminations</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Updates to Terms</h2>
          <p className="text-gray-600 mb-4">
            We may update these terms as our service evolves. Material changes will be communicated via:
          </p>
          <ul className="list-disc list-inside space-y-1 text-gray-600">
            <li>Email notification to all active users</li>
            <li>In-app notifications</li>
            <li>30-day notice period for significant changes</li>
            <li>Updated "Last modified" date at the top</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Governing Law</h2>
          <p className="text-gray-600">
            These terms are governed by the laws of the State of California, United States. 
            Any disputes will be resolved through binding arbitration in San Francisco, CA.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Contact Us</h2>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <p className="text-gray-700 mb-4">
              Questions about these terms? We're here to help clarify anything.
            </p>
            <div className="space-y-2 text-gray-700">
              <p><strong>Email:</strong> legal@bannkmint.ai</p>
              <p><strong>Phone:</strong> +1 (555) 123-4567</p>
              <p><strong>Address:</strong> BannkMint AI Legal Team, 123 Financial District, San Francisco, CA 94105</p>
              <p><strong>Response Time:</strong> We respond to legal inquiries within 2 business days</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default TermsPage;