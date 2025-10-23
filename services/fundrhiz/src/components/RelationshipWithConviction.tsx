'use client'

/**
 * Example: Relationship display with conviction and attestation
 * Shows how to integrate ConvictionBadge and AttestationButton
 */

import React, { useState, useEffect } from 'react'
import { ConvictionBadge } from './ConvictionBadge'
import { AttestationButton } from './AttestationButton'
import { Card } from './ui/Card'

interface Relationship {
  uri: string
  participants: Array<{
    did: string
    name: string
  }>
  type: string
  strength: number
  context?: string
  createdAt: string
}

interface ConvictionData {
  score: number
  attestationCount: number
  verifyCount: number
  disputeCount: number
  trend: 'increasing' | 'stable' | 'decreasing'
}

interface RelationshipWithConvictionProps {
  relationship: Relationship
  showAttestButton?: boolean
}

export function RelationshipWithConviction({
  relationship,
  showAttestButton = true
}: RelationshipWithConvictionProps) {
  const [conviction, setConviction] = useState<ConvictionData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>()

  useEffect(() => {
    loadConviction()
  }, [relationship.uri])

  const loadConviction = async () => {
    try {
      setLoading(true)
      setError(undefined)

      // TODO: Use RhizClient to fetch conviction
      // const client = new RhizClient({ apiUrl: '...' })
      // const result = await client.conviction.getConviction(relationship.uri)
      // setConviction(result.conviction)

      // Simulated data for now
      await new Promise(resolve => setTimeout(resolve, 500))
      setConviction({
        score: 0, // No attestations yet
        attestationCount: 0,
        verifyCount: 0,
        disputeCount: 0,
        trend: 'stable'
      })
    } catch (err) {
      console.error('Failed to load conviction:', err)
      setError(err instanceof Error ? err.message : 'Failed to load conviction')
    } finally {
      setLoading(false)
    }
  }

  const handleAttested = () => {
    // Reload conviction after attestation
    loadConviction()
  }

  return (
    <Card className="p-6">
      {/* Relationship Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold">
            {relationship.participants[0].name} ↔ {relationship.participants[1].name}
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            {relationship.type} relationship • Strength: {relationship.strength}/100
          </p>
        </div>

        {/* Conviction Badge */}
        {!loading && conviction && conviction.attestationCount > 0 && (
          <ConvictionBadge
            score={conviction.score}
            attestationCount={conviction.attestationCount}
            trend={conviction.trend}
          />
        )}
      </div>

      {/* Context */}
      {relationship.context && (
        <p className="text-gray-700 mb-4">
          {relationship.context}
        </p>
      )}

      {/* Conviction Details */}
      {!loading && conviction && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Network Verification</h3>
          {conviction.attestationCount === 0 ? (
            <p className="text-sm text-gray-600">
              No attestations yet. Be the first to verify this relationship!
            </p>
          ) : (
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-600">Verifications:</span>
                <span className="ml-2 font-semibold text-green-600">{conviction.verifyCount}</span>
              </div>
              <div>
                <span className="text-gray-600">Disputes:</span>
                <span className="ml-2 font-semibold text-red-600">{conviction.disputeCount}</span>
              </div>
              <div>
                <span className="text-gray-600">Conviction Score:</span>
                <span className="ml-2 font-semibold">{conviction.score}/100</span>
              </div>
              <div>
                <span className="text-gray-600">Trend:</span>
                <span className="ml-2 font-semibold capitalize">{conviction.trend}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">Loading conviction data...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Attestation Button */}
      {showAttestButton && (
        <div className="flex justify-end">
          <AttestationButton
            relationshipUri={relationship.uri}
            onAttested={handleAttested}
          />
        </div>
      )}

      {/* Metadata */}
      <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
        <p>Created: {new Date(relationship.createdAt).toLocaleDateString()}</p>
        <p className="truncate" title={relationship.uri}>URI: {relationship.uri}</p>
      </div>
    </Card>
  )
}

