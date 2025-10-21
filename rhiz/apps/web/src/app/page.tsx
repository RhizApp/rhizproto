import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero Section */}
      <main className="flex-1">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Fundraising Through{' '}
              <span className="text-primary-600">Relationships</span>
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-gray-600">
              FundRhiz automates warm introductions between founders and investors through
              trust-weighted graph analytics and AI agents. Built on Rhiz Protocol.
            </p>
            <div className="mt-10 flex items-center gap-4">
              <Link href="/dashboard" className="btn-primary">
                Get Started
              </Link>
              <Link href="/about" className="btn-outline">
                Learn More
              </Link>
            </div>
          </div>

          {/* Features Grid */}
          <div className="py-24">
            <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
              <div className="card">
                <div className="mb-4 text-3xl">🔍</div>
                <h3 className="mb-2 text-lg font-semibold">Smart Pathfinding</h3>
                <p className="text-sm text-gray-600">
                  Find the shortest trust-weighted path to any investor through your network.
                </p>
              </div>

              <div className="card">
                <div className="mb-4 text-3xl">🤖</div>
                <h3 className="mb-2 text-lg font-semibold">AI Agents</h3>
                <p className="text-sm text-gray-600">
                  Founder and investor agents pitch, evaluate, and negotiate on your behalf.
                </p>
              </div>

              <div className="card">
                <div className="mb-4 text-3xl">📊</div>
                <h3 className="mb-2 text-lg font-semibold">Trust Metrics</h3>
                <p className="text-sm text-gray-600">
                  Quantified trust scores reveal real social capital and relationship health.
                </p>
              </div>
            </div>
          </div>

          {/* Stats Section */}
          <div className="border-y border-gray-200 py-24">
            <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-primary-600">1K+</div>
                <div className="mt-2 text-sm text-gray-600">Active Users</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-primary-600">10K+</div>
                <div className="mt-2 text-sm text-gray-600">Verified Relationships</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-primary-600">500+</div>
                <div className="mt-2 text-sm text-gray-600">Successful Intros</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-primary-600">$50M+</div>
                <div className="mt-2 text-sm text-gray-600">Capital Raised</div>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="py-24">
            <div className="card mx-auto max-w-3xl bg-primary-600 text-center text-white">
              <h2 className="text-3xl font-bold">Ready to Get Started?</h2>
              <p className="mt-4 text-lg opacity-90">
                Join the relationship-driven fundraising revolution.
              </p>
              <div className="mt-8">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center justify-center rounded-lg bg-white px-6 py-3 text-sm font-medium text-primary-600 hover:bg-gray-100"
                >
                  Launch FundRhiz
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-500">
            <p>© 2025 Rhiz Protocol. Built on open infrastructure.</p>
            <div className="mt-4 flex items-center justify-center gap-6">
              <Link href="/docs" className="hover:text-gray-900">
                Docs
              </Link>
              <Link href="/api" className="hover:text-gray-900">
                API
              </Link>
              <Link href="https://github.com/rhiz/rhiz" className="hover:text-gray-900">
                GitHub
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

