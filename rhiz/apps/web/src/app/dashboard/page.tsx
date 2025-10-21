'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export default function DashboardPage() {
  // Example entity ID - in production this would come from auth
  const entityId = 'demo_user_1';

  const { data: trustHealth, isLoading } = useQuery({
    queryKey: ['trust-health', entityId],
    queryFn: () => api.getTrustHealth(entityId),
    enabled: false, // Disable for demo since entity may not exist
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between">
            <div className="flex">
              <div className="flex flex-shrink-0 items-center">
                <span className="text-xl font-bold text-primary-600">FundRhiz</span>
              </div>
              <div className="ml-6 flex space-x-8">
                <a
                  href="/dashboard"
                  className="inline-flex items-center border-b-2 border-primary-500 px-1 pt-1 text-sm font-medium text-gray-900"
                >
                  Dashboard
                </a>
                <a
                  href="/network"
                  className="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700"
                >
                  Network
                </a>
                <a
                  href="/intros"
                  className="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700"
                >
                  Introductions
                </a>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-600">
            Your relationship intelligence overview
          </p>
        </div>

        {/* Trust Health Summary */}
        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-4">
          <div className="card">
            <div className="text-sm font-medium text-gray-500">Trust Score</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {isLoading ? '...' : trustHealth?.trust_score ? `${Math.round(trustHealth.trust_score * 100)}%` : 'N/A'}
            </div>
            <div className="mt-1 text-xs text-gray-500">
              {trustHealth?.trust_level || 'No data'}
            </div>
          </div>

          <div className="card">
            <div className="text-sm font-medium text-gray-500">Network Size</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {trustHealth?.network_size || 0}
            </div>
            <div className="mt-1 text-xs text-gray-500">Connections</div>
          </div>

          <div className="card">
            <div className="text-sm font-medium text-gray-500">Verified</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {trustHealth?.verified_ratio
                ? `${Math.round(trustHealth.verified_ratio * 100)}%`
                : '0%'}
            </div>
            <div className="mt-1 text-xs text-gray-500">Of relationships</div>
          </div>

          <div className="card">
            <div className="text-sm font-medium text-gray-500">Recent Activity</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {trustHealth?.recent_activity || 0}
            </div>
            <div className="mt-1 text-xs text-gray-500">Last 30 days</div>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Quick Actions */}
          <div className="card">
            <h2 className="mb-4 text-lg font-semibold">Quick Actions</h2>
            <div className="space-y-2">
              <button className="btn-primary w-full justify-start">
                🎯 Request Introduction
              </button>
              <button className="btn-outline w-full justify-start">
                👥 Explore Network
              </button>
              <button className="btn-outline w-full justify-start">
                📊 View Analytics
              </button>
            </div>
          </div>

          {/* Recommendations */}
          <div className="card">
            <h2 className="mb-4 text-lg font-semibold">Recommendations</h2>
            {trustHealth?.recommendations && trustHealth.recommendations.length > 0 ? (
              <ul className="space-y-2">
                {trustHealth.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="text-primary-500">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">
                Looking good! Keep building relationships.
              </p>
            )}
          </div>

          {/* Recent Introductions */}
          <div className="card">
            <h2 className="mb-4 text-lg font-semibold">Recent Introductions</h2>
            <div className="text-center text-sm text-gray-500 py-8">
              No recent introductions. Start connecting!
            </div>
          </div>

          {/* Network Activity */}
          <div className="card">
            <h2 className="mb-4 text-lg font-semibold">Network Activity</h2>
            <div className="text-center text-sm text-gray-500 py-8">
              Activity feed coming soon
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

