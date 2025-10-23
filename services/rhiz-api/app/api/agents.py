"""
Protocol Agent API Endpoints

AI-powered protocol features:
- Relationship extraction from text
- Trust score explanations
- Introduction orchestration

These are protocol-level features, not application features.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.protocol_agents import get_protocol_agent_service

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


# ==========================================
# Relationship Extraction Endpoints
# ==========================================

class ExtractRelationshipsRequest(BaseModel):
    """Request to extract relationships from text"""
    
    text: str = Field(..., description="Unstructured text containing relationship information")
    context_hint: Optional[str] = Field(None, description="Optional context to guide extraction")


class ExtractRelationshipsResponse(BaseModel):
    """Response with extracted relationships"""
    
    relationships: List[Dict[str, Any]]
    total_found: int
    extraction_quality: int
    ambiguous_cases: List[str]


@router.post("/relationships/extract", response_model=ExtractRelationshipsResponse)
async def extract_relationships(request: ExtractRelationshipsRequest):
    """
    Extract structured relationship data from unstructured text
    
    This protocol feature allows extracting machine-readable relationships
    from natural language text (bios, profiles, descriptions, etc.).
    
    Example:
        Input: "Alice and Bob co-founded TechCo in 2020 and worked together for 3 years"
        Output: Structured relationship record with participants, type, strength, context
    """
    try:
        agent_service = get_protocol_agent_service()
        result = await agent_service.extract_relationships_from_text(
            text=request.text, context_hint=request.context_hint
        )
        
        # Convert to dict for response
        return ExtractRelationshipsResponse(
            relationships=[rel.model_dump() for rel in result.relationships],
            total_found=result.total_found,
            extraction_quality=result.extraction_quality,
            ambiguous_cases=result.ambiguous_cases,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Relationship extraction failed: {str(e)}",
        )


class AssessQualityRequest(BaseModel):
    """Request to assess relationship quality"""
    
    relationship_context: str = Field(..., description="Description of the relationship")
    claimed_strength: int = Field(..., ge=0, le=100, description="Claimed strength score (0-100)")


class AssessQualityResponse(BaseModel):
    """Response with quality assessment"""
    
    has_sufficient_context: bool
    has_quantifiable_metrics: bool
    has_verification_potential: bool
    strength_justification: str
    suggested_improvements: List[str]
    quality_score: int
    attestation_potential: int


@router.post("/relationships/assess-quality", response_model=AssessQualityResponse)
async def assess_relationship_quality(request: AssessQualityRequest):
    """
    Assess the quality of a relationship description
    
    Evaluates whether the relationship context justifies the claimed strength
    and provides suggestions for improvement.
    """
    try:
        agent_service = get_protocol_agent_service()
        result = await agent_service.assess_relationship_quality(
            relationship_context=request.relationship_context,
            claimed_strength=request.claimed_strength,
        )
        
        return AssessQualityResponse(
            has_sufficient_context=result.has_sufficient_context,
            has_quantifiable_metrics=result.has_quantifiable_metrics,
            has_verification_potential=result.has_verification_potential,
            strength_justification=result.strength_justification,
            suggested_improvements=result.suggested_improvements,
            quality_score=result.quality_score,
            attestation_potential=result.attestation_potential,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality assessment failed: {str(e)}",
        )


# ==========================================
# Trust Explanation Endpoints
# ==========================================

class ExplainTrustRequest(BaseModel):
    """Request to explain trust score"""
    
    entity_did: str = Field(..., description="DID of the entity")
    trust_metrics: Dict[str, Any] = Field(..., description="Trust metrics data")
    network_context: Dict[str, Any] = Field(..., description="Network statistics for comparison")


class ExplainTrustResponse(BaseModel):
    """Response with trust explanation"""
    
    overall_trust_score: int
    explanation_summary: str
    breakdown: List[Dict[str, Any]]
    strengths: List[str]
    concerns: List[str]
    comparison_to_network: str
    trend: str
    recommendation: str


@router.post("/trust/explain", response_model=ExplainTrustResponse)
async def explain_trust_score(request: ExplainTrustRequest):
    """
    Generate human-readable explanation of trust score
    
    Breaks down trust metrics into understandable components and
    provides context relative to the network.
    """
    try:
        agent_service = get_protocol_agent_service()
        result = await agent_service.explain_trust_score(
            entity_did=request.entity_did,
            trust_metrics=request.trust_metrics,
            network_context=request.network_context,
        )
        
        return ExplainTrustResponse(
            overall_trust_score=result.overall_trust_score,
            explanation_summary=result.explanation_summary,
            breakdown=[b.model_dump() for b in result.breakdown],
            strengths=result.strengths,
            concerns=result.concerns,
            comparison_to_network=result.comparison_to_network,
            trend=result.trend,
            recommendation=result.recommendation,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trust explanation failed: {str(e)}",
        )


class ExplainConvictionRequest(BaseModel):
    """Request to explain conviction score"""
    
    relationship_uri: str = Field(..., description="AT URI of the relationship")
    conviction_data: Dict[str, Any] = Field(..., description="Conviction calculation data")
    attestations: List[Dict[str, Any]] = Field(..., description="List of attestations")


class ExplainConvictionResponse(BaseModel):
    """Response with conviction explanation"""
    
    conviction_score: int
    confidence_level: str
    attestation_summary: str
    key_attesters: List[str]
    positive_signals: List[str]
    negative_signals: List[str]
    recommendation: str
    verification_status: str


@router.post("/trust/explain-conviction", response_model=ExplainConvictionResponse)
async def explain_conviction_score(request: ExplainConvictionRequest):
    """
    Explain conviction score for a relationship
    
    Describes why a relationship has its network confidence score
    based on attestations and attester reputation.
    """
    try:
        agent_service = get_protocol_agent_service()
        result = await agent_service.explain_conviction_score(
            relationship_uri=request.relationship_uri,
            conviction_data=request.conviction_data,
            attestations=request.attestations,
        )
        
        return ExplainConvictionResponse(
            conviction_score=result.conviction_score,
            confidence_level=result.confidence_level,
            attestation_summary=result.attestation_summary,
            key_attesters=result.key_attesters,
            positive_signals=result.positive_signals,
            negative_signals=result.negative_signals,
            recommendation=result.recommendation,
            verification_status=result.verification_status,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conviction explanation failed: {str(e)}",
        )


class ExplainPathRequest(BaseModel):
    """Request to explain path choice"""
    
    from_did: str = Field(..., description="Starting entity DID")
    to_did: str = Field(..., description="Target entity DID")
    chosen_path: Dict[str, Any] = Field(..., description="The selected path data")
    alternative_paths: List[Dict[str, Any]] = Field(..., description="Other considered paths")
    selection_criteria: str = Field(..., description="Criteria used for selection")


class ExplainPathResponse(BaseModel):
    """Response with path explanation"""
    
    path_strength: int
    hop_count: int
    why_optimal: str
    relationship_quality: List[str]
    alternative_paths_considered: int
    why_others_rejected: str
    risk_factors: List[str]
    success_probability: int
    strategy_recommendation: str


@router.post("/trust/explain-path", response_model=ExplainPathResponse)
async def explain_path_choice(request: ExplainPathRequest):
    """
    Explain why a particular introduction path was chosen
    
    Describes the tradeoffs between different paths and why
    the chosen path is optimal.
    """
    try:
        agent_service = get_protocol_agent_service()
        result = await agent_service.explain_path_choice(
            from_did=request.from_did,
            to_did=request.to_did,
            chosen_path=request.chosen_path,
            alternative_paths=request.alternative_paths,
            selection_criteria=request.selection_criteria,
        )
        
        return ExplainPathResponse(
            path_strength=result.path_strength,
            hop_count=result.hop_count,
            why_optimal=result.why_optimal,
            relationship_quality=result.relationship_quality,
            alternative_paths_considered=result.alternative_paths_considered,
            why_others_rejected=result.why_others_rejected,
            risk_factors=result.risk_factors,
            success_probability=result.success_probability,
            strategy_recommendation=result.strategy_recommendation,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Path explanation failed: {str(e)}",
        )


# ==========================================
# Introduction Orchestration Endpoints
# ==========================================

class GenerateIntroRequestModel(BaseModel):
    """Request to generate introduction request"""
    
    requester_did: str
    requester_context: str
    intermediary_did: str
    intermediary_context: str
    target_did: str
    target_context: str
    introduction_purpose: str
    relationship_data: Dict[str, Any]


class IntroductionMessageResponse(BaseModel):
    """Response with introduction message"""
    
    recipient_did: str
    recipient_name: str
    subject_line: str
    message_body: str
    message_tone: Dict[str, str]
    context_highlights: List[Dict[str, Any]]
    call_to_action: str
    optimal_send_time: str
    followup_timing_days: int
    success_probability: int
    personalization_score: int


@router.post("/intros/generate-request", response_model=IntroductionMessageResponse)
async def generate_intro_request(request: GenerateIntroRequestModel):
    """
    Generate personalized introduction request message
    
    Creates a tailored message asking an intermediary to facilitate
    an introduction through the trust network.
    """
    try:
        agent_service = get_protocol_agent_service()
        result = await agent_service.generate_intro_request(
            requester_did=request.requester_did,
            requester_context=request.requester_context,
            intermediary_did=request.intermediary_did,
            intermediary_context=request.intermediary_context,
            target_did=request.target_did,
            target_context=request.target_context,
            introduction_purpose=request.introduction_purpose,
            relationship_data=request.relationship_data,
        )
        
        return IntroductionMessageResponse(
            recipient_did=result.recipient_did,
            recipient_name=result.recipient_name,
            subject_line=result.subject_line,
            message_body=result.message_body,
            message_tone=result.message_tone.model_dump(),
            context_highlights=[h.model_dump() for h in result.context_highlights],
            call_to_action=result.call_to_action,
            optimal_send_time=result.optimal_send_time,
            followup_timing_days=result.followup_timing_days,
            success_probability=result.success_probability,
            personalization_score=result.personalization_score,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intro request generation failed: {str(e)}",
        )


class PlanOrchestrationRequest(BaseModel):
    """Request to plan introduction orchestration"""
    
    requester_did: str
    target_did: str
    intro_path: List[str]
    relationship_data: Dict[str, Any]
    introduction_purpose: str


class OrchestrationPlanResponse(BaseModel):
    """Response with orchestration plan"""
    
    total_steps: int
    steps: List[Dict[str, Any]]
    timeline_days: int
    success_probability: int
    risk_factors: List[str]
    mitigation_strategies: List[str]
    alternative_paths: List[str]


@router.post("/intros/plan-orchestration", response_model=OrchestrationPlanResponse)
async def plan_intro_orchestration(request: PlanOrchestrationRequest):
    """
    Plan multi-step introduction orchestration
    
    Creates a step-by-step plan for orchestrating an introduction
    through multiple intermediaries in the trust network.
    """
    try:
        agent_service = get_protocol_agent_service()
        result = await agent_service.plan_intro_orchestration(
            requester_did=request.requester_did,
            target_did=request.target_did,
            intro_path=request.intro_path,
            relationship_data=request.relationship_data,
            introduction_purpose=request.introduction_purpose,
        )
        
        return OrchestrationPlanResponse(
            total_steps=result.total_steps,
            steps=[s.model_dump() for s in result.steps],
            timeline_days=result.timeline_days,
            success_probability=result.success_probability,
            risk_factors=result.risk_factors,
            mitigation_strategies=result.mitigation_strategies,
            alternative_paths=result.alternative_paths,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration planning failed: {str(e)}",
        )


class AssessFeasibilityRequest(BaseModel):
    """Request to assess introduction feasibility"""
    
    requester_did: str
    target_did: str
    proposed_path: Dict[str, Any]
    relationship_data: Dict[str, Any]
    introduction_purpose: str
    timing_context: Optional[str] = None


class FeasibilityResponse(BaseModel):
    """Response with feasibility assessment"""
    
    feasibility_score: int
    feasibility_level: str
    success_factors: List[str]
    blocking_factors: List[str]
    recommended_approach: str
    timing_recommendation: str
    alternative_suggestions: List[str]


@router.post("/intros/assess-feasibility", response_model=FeasibilityResponse)
async def assess_intro_feasibility(request: AssessFeasibilityRequest):
    """
    Assess feasibility of introduction before attempting
    
    Evaluates whether an introduction is likely to succeed
    and provides recommendations.
    """
    try:
        agent_service = get_protocol_agent_service()
        result = await agent_service.assess_intro_feasibility(
            requester_did=request.requester_did,
            target_did=request.target_did,
            proposed_path=request.proposed_path,
            relationship_data=request.relationship_data,
            introduction_purpose=request.introduction_purpose,
            timing_context=request.timing_context,
        )
        
        return FeasibilityResponse(
            feasibility_score=result.feasibility_score,
            feasibility_level=result.feasibility_level,
            success_factors=result.success_factors,
            blocking_factors=result.blocking_factors,
            recommended_approach=result.recommended_approach,
            timing_recommendation=result.timing_recommendation,
            alternative_suggestions=result.alternative_suggestions,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feasibility assessment failed: {str(e)}",
        )

