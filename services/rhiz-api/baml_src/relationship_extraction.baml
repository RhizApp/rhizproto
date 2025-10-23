// Relationship Extraction for Rhiz Protocol
// Extract structured relationship data from unstructured text

class ExtractedRelationship {
  participant_a_name string
  participant_a_handle string?
  participant_b_name string
  participant_b_handle string?
  
  relationship_type string  // "professional" | "personal" | "academic" | "transactional" | "organizational"
  relationship_strength int  // 0-100
  
  context string  // Brief description of how they know each other
  duration_years float?
  
  evidence string[]  // Specific facts that support this relationship
  confidence_score int  // 0-100, how confident in this extraction
}

class RelationshipExtractionResult {
  relationships ExtractedRelationship[]
  total_found int
  extraction_quality int  // 0-100
  ambiguous_cases string[]  // Cases that need human review
}

function ExtractRelationshipsFromText(
  text: string,
  context_hint: string?
) -> RelationshipExtractionResult {
  client GPT4
  prompt #"
    Extract all relationships mentioned in this text.
    
    TEXT:
    {{ text }}
    
    {% if context_hint %}
    CONTEXT: {{ context_hint }}
    {% endif %}
    
    For each relationship found, extract:
    1. Both participants (names and handles if mentioned)
    2. Type of relationship (professional, personal, academic, etc.)
    3. Relationship strength (0-100, based on described closeness)
    4. Context (how they know each other)
    5. Duration if mentioned
    6. Specific evidence supporting the relationship
    7. Your confidence in this extraction (0-100)
    
    Rules:
    - Only extract explicit relationships (not inferred)
    - Strength scoring:
      * 90-100: Deep, long-term relationships (co-founders, close collaborators)
      * 70-89: Strong professional relationships (colleagues, regular collaborators)
      * 50-69: Established connections (worked together, know well)
      * 30-49: Acquaintances (met multiple times, loose connection)
      * 0-29: Minimal connection (met once, brief interaction)
    
    Flag ambiguous cases where human review is needed.
    
    Return structured JSON matching RelationshipExtractionResult schema.
  "#
}

// Assess quality of a relationship description
class RelationshipQualityAssessment {
  has_sufficient_context bool
  has_quantifiable_metrics bool
  has_verification_potential bool
  
  strength_justification string
  suggested_improvements string[]
  
  quality_score int  // 0-100, overall quality of relationship data
  attestation_potential int  // 0-100, how likely others could attest
}

function AssessRelationshipQuality(
  relationship_context: string,
  claimed_strength: int
) -> RelationshipQualityAssessment {
  client GPT4Mini
  prompt #"
    Assess the quality of this relationship description.
    
    CONTEXT: {{ relationship_context }}
    CLAIMED STRENGTH: {{ claimed_strength }}
    
    Evaluate:
    1. Does the context justify the claimed strength?
    2. Is there sufficient detail for verification?
    3. Are there quantifiable metrics (time, projects, outcomes)?
    4. Could third parties reasonably attest to this?
    
    Provide:
    - Quality assessment (bool checks)
    - Justification for strength score
    - Suggestions to improve relationship data quality
    - Overall quality score (0-100)
    - Attestation potential (how verifiable)
    
    Return structured JSON matching RelationshipQualityAssessment schema.
  "#
}

