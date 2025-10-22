'use client'

/**
 * AttestationButton Component
 * Allows users to attest to relationships
 */

import React, { useState } from 'react'
import { Button } from './ui/Button'

interface AttestationButtonProps {
  relationshipUri: string
  onAttested?: () => void
  className?: string
}

export function AttestationButton({ 
  relationshipUri, 
  onAttested,
  className = '' 
}: AttestationButtonProps) {
  const [showForm, setShowForm] = useState(false)
  const [type, setType] = useState<'verify' | 'dispute' | 'strengthen' | 'weaken'>('verify')
  const [confidence, setConfidence] = useState(80)
  const [evidence, setEvidence] = useState('')
  const [suggestedStrength, setSuggestedStrength] = useState<number>()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string>()

  const handleSubmit = async () => {
    setError(undefined)
    setSubmitting(true)

    try {
      // TODO: Initialize RhizClient with session
      // For now, just simulate
      console.log('Submitting attestation:', {
        targetRelationship: relationshipUri,
        attestationType: type,
        confidence,
        evidence: evidence.trim() || undefined,
        suggestedStrength: type === 'strengthen' || type === 'weaken' ? suggestedStrength : undefined
      })

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))

      setShowForm(false)
      setEvidence('')
      setSuggestedStrength(undefined)
      onAttested?.()
      
      alert('Attestation submitted successfully!')
    } catch (err) {
      console.error('Failed to submit attestation:', err)
      setError(err instanceof Error ? err.message : 'Failed to submit attestation')
    } finally {
      setSubmitting(false)
    }
  }

  if (!showForm) {
    return (
      <Button 
        onClick={() => setShowForm(true)}
        className={className}
        variant="outline"
      >
        Attest to this relationship
      </Button>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
        <h3 className="text-xl font-bold mb-4">Attest to Relationship</h3>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded text-red-800 text-sm">
            {error}
          </div>
        )}
        
        {/* Attestation Type */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Attestation Type
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                value="verify"
                checked={type === 'verify'}
                onChange={(e) => setType(e.target.value as any)}
                className="mr-2"
              />
              <span className="text-sm">
                <strong>Verify</strong> - I confirm this relationship exists as stated
              </span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="dispute"
                checked={type === 'dispute'}
                onChange={(e) => setType(e.target.value as any)}
                className="mr-2"
              />
              <span className="text-sm">
                <strong>Dispute</strong> - I don't believe this is accurate
              </span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="strengthen"
                checked={type === 'strengthen'}
                onChange={(e) => setType(e.target.value as any)}
                className="mr-2"
              />
              <span className="text-sm">
                <strong>Strengthen</strong> - The relationship is stronger than stated
              </span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="weaken"
                checked={type === 'weaken'}
                onChange={(e) => setType(e.target.value as any)}
                className="mr-2"
              />
              <span className="text-sm">
                <strong>Weaken</strong> - The relationship is weaker than stated
              </span>
            </label>
          </div>
        </div>

        {/* Confidence Slider */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Confidence: <span className="font-bold">{confidence}%</span>
          </label>
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={confidence}
            onChange={(e) => setConfidence(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Not sure</span>
            <span>Very confident</span>
          </div>
        </div>

        {/* Suggested Strength (for strengthen/weaken) */}
        {(type === 'strengthen' || type === 'weaken') && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Suggested Strength: {suggestedStrength ?? 'Not set'}
            </label>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={suggestedStrength ?? 50}
              onChange={(e) => setSuggestedStrength(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        )}

        {/* Evidence */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Evidence (optional but recommended)
          </label>
          <textarea
            value={evidence}
            onChange={(e) => setEvidence(e.target.value)}
            placeholder="e.g., 'I worked with both of them at TechCo for 2 years'"
            maxLength={1000}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
          <p className="text-xs text-gray-500 mt-1">
            {evidence.length}/1000 characters
          </p>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <Button 
            variant="outline" 
            onClick={() => setShowForm(false)}
            disabled={submitting}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={submitting}
          >
            {submitting ? 'Submitting...' : 'Submit Attestation'}
          </Button>
        </div>
      </div>
    </div>
  )
}

