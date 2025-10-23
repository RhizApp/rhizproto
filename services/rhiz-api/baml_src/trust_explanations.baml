// Trust Score Explanations for Rhiz Protocol
// Generate human-readable explanations of trust calculations

class TrustScoreBreakdown {
  component string  // "reciprocity" | "consistency" | "reputation" | "conviction"
  score int  // 0-100
  weight float  // How much this contributes to overall
  explanation string
  key_factors string[]
}

class TrustExplanation {
  overall_trust_score int
  explanation_summary string
  
  breakdown TrustScoreBreakdown[]
  
  strengths string[]  // What makes this entity trustworthy
  concerns string[]   // What could improve
  
  comparison_to_network string  // How they compare to average
  trend string  // "improving" | "stable" | "declining"
  
  recommendation string  // Should others trust this entity?
}

function ExplainTrustScore(
  entity_did: string,
  trust_metrics: string,  // JSON of TrustMetrics
  network_context: string  // JSON of network stats for comparison
) -> TrustExplanation {
  client GPT4
  prompt #"
    Generate a human-readable explanation of this trust score.
    
    ENTITY: {{ entity_did }}
    
    TRUST METRICS:
    {{ trust_metrics }}
    
    NETWORK CONTEXT:
    {{ network_context }}
    
    Explain in clear language:
    1. What the overall trust score means
    2. How each component contributes
    3. Key factors driving the score
    4. Strengths (what's working well)
    5. Concerns (what could improve)
    6. How this compares to network average
    7. Whether trust is improving, stable, or declining
    8. Overall recommendation
    
    Make it accessible to non-technical users.
    Avoid jargon - use plain language.
    Be specific with examples where possible.
    
    Return structured JSON matching TrustExplanation schema.
  "#
}

// Explain conviction score for a relationship
class ConvictionExplanation {
  conviction_score int
  confidence_level string  // "very_high" | "high" | "moderate" | "low" | "very_low"
  
  attestation_summary string
  key_attesters string[]  // Names/DIDs of notable attesters
  
  positive_signals string[]
  negative_signals string[]
  
  recommendation string  // Should this relationship be trusted?
  verification_status string  // "strong" | "moderate" | "weak" | "unverified"
}

function ExplainConvictionScore(
  relationship_uri: string,
  conviction_data: string,  // JSON of conviction calculation
  attestations: string  // JSON array of attestations
) -> ConvictionExplanation {
  client GPT4
  prompt #"
    Explain why this relationship has its conviction score.
    
    RELATIONSHIP: {{ relationship_uri }}
    
    CONVICTION DATA:
    {{ conviction_data }}
    
    ATTESTATIONS:
    {{ attestations }}
    
    Explain:
    1. What the conviction score means (network confidence in this relationship)
    2. Who attested to it (particularly high-reputation attesters)
    3. Positive signals (verify attestations, high-reputation attesters, etc.)
    4. Negative signals (disputes, low attestation count, etc.)
    5. Overall confidence level
    6. Recommendation on trusting this relationship
    7. Verification status
    
    Use plain language. Be balanced in assessment.
    
    Return structured JSON matching ConvictionExplanation schema.
  "#
}

// Explain why a path was chosen for an introduction
class PathExplanation {
  path_strength int
  hop_count int
  
  why_optimal string  // Why this path was chosen
  relationship_quality string[]  // Quality of each hop
  
  alternative_paths_considered int
  why_others_rejected string
  
  risk_factors string[]
  success_probability int  // 0-100
  
  strategy_recommendation string
}

function ExplainPathChoice(
  from_did: string,
  to_did: string,
  chosen_path: string,  // JSON of path with hops
  alternative_paths: string,  // JSON of other considered paths
  selection_criteria: string
) -> PathExplanation {
  client GPT4Mini
  prompt #"
    Explain why this introduction path was selected.
    
    FROM: {{ from_did }}
    TO: {{ to_did }}
    
    CHOSEN PATH:
    {{ chosen_path }}
    
    ALTERNATIVES:
    {{ alternative_paths }}
    
    SELECTION CRITERIA:
    {{ selection_criteria }}
    
    Explain:
    1. Why this path is optimal (balance of strength, hops, feasibility)
    2. Quality of each relationship in the path
    3. How many alternatives were considered
    4. Why alternatives were rejected
    5. Risk factors in this path
    6. Estimated success probability
    7. Strategic recommendations for using this path
    
    Be specific about the tradeoffs involved.
    
    Return structured JSON matching PathExplanation schema.
  "#
}

