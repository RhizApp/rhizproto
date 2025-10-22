/**
 * ConvictionBadge Component
 * Displays conviction score with color coding and trend indicator
 */

import React from 'react'

interface ConvictionBadgeProps {
  score: number
  attestationCount: number
  trend?: 'increasing' | 'stable' | 'decreasing'
  className?: string
  showDetails?: boolean
}

export function ConvictionBadge({ 
  score, 
  attestationCount, 
  trend = 'stable',
  className = '',
  showDetails = true
}: ConvictionBadgeProps) {
  // Color based on score
  const getColorClasses = (score: number) => {
    if (score >= 80) return 'bg-green-100 text-green-800 border-green-300'
    if (score >= 60) return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    if (score >= 40) return 'bg-orange-100 text-orange-800 border-orange-300'
    return 'bg-red-100 text-red-800 border-red-300'
  }
  
  // Trend icon
  const trendIcon = {
    increasing: '↗',
    stable: '→',
    decreasing: '↘'
  }[trend]
  
  const trendColor = {
    increasing: 'text-green-600',
    stable: 'text-gray-500',
    decreasing: 'text-red-600'
  }[trend]

  return (
    <div 
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${getColorClasses(score)} ${className}`}
      title={`Network conviction: ${score}/100 based on ${attestationCount} attestation${attestationCount === 1 ? '' : 's'}`}
    >
      <span className="font-bold text-lg">{score}%</span>
      {showDetails && (
        <>
          <span className="text-xs font-medium opacity-90">verified</span>
          <span className={`text-sm ${trendColor}`}>{trendIcon}</span>
          <span className="text-xs opacity-75">
            {attestationCount} {attestationCount === 1 ? 'attestation' : 'attestations'}
          </span>
        </>
      )}
    </div>
  )
}

/**
 * Compact version for use in lists
 */
export function ConvictionBadgeCompact({ score, className = '' }: { score: number, className?: string }) {
  const getColorClasses = (score: number) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    if (score >= 40) return 'bg-orange-500'
    return 'bg-red-500'
  }

  return (
    <div 
      className={`inline-flex items-center justify-center w-12 h-12 rounded-full ${getColorClasses(score)} text-white font-bold ${className}`}
      title={`Conviction: ${score}%`}
    >
      {score}
    </div>
  )
}

