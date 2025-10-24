'use client'

import { useEffect, useState } from 'react'
import {
  opportunityService,
  type Opportunity,
} from '@/services/opportunities/opportunityService'

const OpportunityTypeIcon: Record<Opportunity['type'], string> = {
  accelerator: '🚀',
  grant: '💰',
  investor: '💼',
  event: '🎪',
  competition: '🏆',
  community: '👥',
}

const OpportunityTypeBadge: Record<Opportunity['type'], string> = {
  accelerator: 'bg-purple-100 text-purple-800',
  grant: 'bg-green-100 text-green-800',
  investor: 'bg-blue-100 text-blue-800',
  event: 'bg-orange-100 text-orange-800',
  competition: 'bg-pink-100 text-pink-800',
  community: 'bg-indigo-100 text-indigo-800',
}

export default function OpportunityFeed() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<Opportunity['type'] | 'all'>('all')

  const loadOpportunities = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await opportunityService.discoverOpportunities(
        filter !== 'all' ? { type: filter } : undefined,
      )
      setOpportunities(data)
    } catch (err) {
      setError('Failed to load opportunities')
      console.error('Error loading opportunities:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadOpportunities()
  }, [filter])

  if (loading) {
    return (
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold">Opportunities for You</h2>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="mb-2 h-4 w-3/4 rounded bg-gray-200"></div>
              <div className="mb-1 h-3 w-full rounded bg-gray-200"></div>
              <div className="h-3 w-5/6 rounded bg-gray-200"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold">Opportunities for You</h2>
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center">
          <p className="text-sm text-red-800">{error}</p>
          <button
            onClick={loadOpportunities}
            className="mt-2 text-sm font-medium text-red-600 hover:underline"
          >
            Try again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Opportunities for You</h2>
        <select
          value={filter}
          onChange={(e) =>
            setFilter(e.target.value as Opportunity['type'] | 'all')
          }
          className="rounded-md border border-gray-300 px-2 py-1 text-sm"
          aria-label="Filter opportunities by type"
        >
          <option value="all">All Types</option>
          <option value="accelerator">Accelerators</option>
          <option value="grant">Grants</option>
          <option value="investor">Investors</option>
          <option value="event">Events</option>
          <option value="competition">Competitions</option>
          <option value="community">Communities</option>
        </select>
      </div>

      <div className="max-h-[600px] space-y-4 overflow-y-auto">
        {opportunities.length === 0 ? (
          <p className="py-8 text-center text-gray-500">
            No opportunities found for this filter.
          </p>
        ) : (
          opportunities.map((opp) => (
            <div
              key={opp.id}
              className="hover:border-primary-300 rounded-lg border border-gray-200 p-4 transition-all hover:shadow-sm"
            >
              <div className="mb-2 flex items-start justify-between">
                <div className="flex flex-1 items-start gap-3">
                  <span className="text-2xl">
                    {OpportunityTypeIcon[opp.type]}
                  </span>
                  <div className="flex-1">
                    <h3 className="mb-1 font-semibold text-gray-900">
                      {opp.title}
                    </h3>
                    <div className="mb-2 flex flex-wrap items-center gap-2">
                      <span
                        className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${
                          OpportunityTypeBadge[opp.type]
                        }`}
                      >
                        {opp.type.charAt(0).toUpperCase() + opp.type.slice(1)}
                      </span>
                      {opp.matchScore && (
                        <span className="bg-primary-100 text-primary-800 inline-flex items-center rounded px-2 py-0.5 text-xs font-medium">
                          {opp.matchScore}% match
                        </span>
                      )}
                      {opp.amount && (
                        <span className="text-xs font-medium text-gray-600">
                          {opp.amount}
                        </span>
                      )}
                    </div>
                    <p className="mb-2 text-sm text-gray-600">
                      {opp.description}
                    </p>
                    <div className="mb-2 flex items-center gap-3 text-xs text-gray-500">
                      <span>📍 {opp.location}</span>
                      {opp.deadline && <span>⏰ {opp.deadline}</span>}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {opp.tags.slice(0, 4).map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-700"
                        >
                          {tag}
                        </span>
                      ))}
                      {opp.tags.length > 4 && (
                        <span className="text-xs text-gray-500">
                          +{opp.tags.length - 4} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between">
                <span className="text-xs text-gray-600">by {opp.provider}</span>
                <a
                  href={opp.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-700 bg-primary-50 hover:bg-primary-100 inline-flex items-center rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
                >
                  Learn More →
                </a>
              </div>
            </div>
          ))
        )}
      </div>

      {opportunities.length > 0 && (
        <div className="mt-4 border-t border-gray-200 pt-4 text-center">
          <p className="text-xs text-gray-500">
            Showing {opportunities.length} opportunities • Updated daily
          </p>
        </div>
      )}
    </div>
  )
}
