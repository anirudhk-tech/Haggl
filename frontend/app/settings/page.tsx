'use client';

import { useRouter } from 'next/navigation';
import { ArrowRight } from 'lucide-react';

export default function Settings() {
  const router = useRouter();

  const handleReOnboard = () => {
    localStorage.removeItem('onboarding_complete');
    router.push('/onboarding');
  };

  return (
    <div className="max-w-[1100px] mx-auto px-16 py-12">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Settings</h1>

      <div className="space-y-8">
        {/* Profile Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Profile</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Business Name</label>
              <input
                type="text"
                defaultValue="Sweet Dreams Bakery"
                className="w-full border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Email</label>
              <input
                type="email"
                defaultValue="contact@sweetdreams.com"
                className="w-full border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Phone</label>
              <input
                type="tel"
                defaultValue="+1 (555) 123-4567"
                className="w-full border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand"
              />
            </div>
          </div>
          <button className="mt-6 bg-brand hover:bg-brand-dark text-white font-medium px-4 py-2.5 rounded-lg transition-colors">
            Save Changes
          </button>
        </div>

        {/* Notifications Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Notifications</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">Email Notifications</p>
                <p className="text-xs text-gray-500">Receive email updates about order status</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded border-gray-300 text-brand focus:ring-brand" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">SMS Notifications</p>
                <p className="text-xs text-gray-500">Receive SMS for urgent approvals</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded border-gray-300 text-brand focus:ring-brand" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">Order Updates</p>
                <p className="text-xs text-gray-500">Get notified when agents complete tasks</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded border-gray-300 text-brand focus:ring-brand" />
            </div>
          </div>
        </div>

        {/* Preferences Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Preferences</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Default Currency</label>
              <select className="w-full border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand">
                <option>USD ($)</option>
                <option>EUR (€)</option>
                <option>GBP (£)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Time Zone</label>
              <select className="w-full border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand">
                <option>Pacific Time (PT)</option>
                <option>Mountain Time (MT)</option>
                <option>Central Time (CT)</option>
                <option>Eastern Time (ET)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Onboarding Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Setup</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-900">Business Setup</p>
                <p className="text-xs text-gray-500">Update your company type and product list</p>
              </div>
              <button
                onClick={handleReOnboard}
                className="flex items-center gap-2 text-brand hover:text-brand-dark text-sm font-medium"
              >
                Re-run Setup
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

