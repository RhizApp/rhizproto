"""
Protocol-level agent services for Rhiz

These agents provide AI-powered capabilities at the protocol layer:
- Relationship extraction from unstructured text
- Trust score explanations
- Introduction orchestration and messaging

These are protocol features, not application features.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from app.generated.baml_client import b
from app.generated.baml_client.types import (
    RelationshipExtractionResult,
    ExtractedRelationship,
    RelationshipQualityAssessment,
    TrustExplanation,
    ConvictionExplanation,
    PathExplanation,
    IntroductionMessage,
    ForwardingIntro,
    FollowupMessage,
    IntroOrchestrationPlan,
    IntroFeasibility,
)

logger = logging.getLogger(__name__)


class ProtocolAgentService:
    """
    Service wrapper for BAML protocol agents

    Provides type-safe, tested interfaces to AI functions for:
    - Relationship data extraction
    - Trust metric explanations
    - Introduction orchestration
    """

    def __init__(self):
        """Initialize the protocol agent service"""
        self.client = b
        logger.info("Protocol agent service initialized")

    # ==========================================
    # Relationship Extraction
    # ==========================================

    async def extract_relationships_from_text(
        self, text: str, context_hint: Optional[str] = None
    ) -> RelationshipExtractionResult:
        """
        Extract structured relationship data from unstructured text

        Args:
            text: Unstructured text containing relationship information
            context_hint: Optional context to guide extraction

        Returns:
            RelationshipExtractionResult with extracted relationships

        Example:
            >>> result = await service.extract_relationships_from_text(
            ...     "Alice and Bob co-founded TechCo in 2020 and worked together for 3 years"
            ... )
            >>> print(result.relationships[0].context)
        """
        try:
            logger.info(f"Extracting relationships from text ({len(text)} chars)")
            result = await self.client.ExtractRelationshipsFromText(
                text=text, context_hint=context_hint
            )
            logger.info(f"Extracted {result.total_found} relationships")
            return result
        except Exception as e:
            logger.error(f"Relationship extraction failed: {e}")
            raise

    async def assess_relationship_quality(
        self, relationship_context: str, claimed_strength: int
    ) -> RelationshipQualityAssessment:
        """
        Assess the quality of a relationship description

        Args:
            relationship_context: Description of the relationship
            claimed_strength: Claimed strength score (0-100)

        Returns:
            RelationshipQualityAssessment with quality metrics
        """
        try:
            logger.info(f"Assessing relationship quality (strength={claimed_strength})")
            result = await self.client.AssessRelationshipQuality(
                relationship_context=relationship_context,
                claimed_strength=claimed_strength,
            )
            logger.info(f"Quality score: {result.quality_score}/100")
            return result
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            raise

    # ==========================================
    # Trust Explanations
    # ==========================================

    async def explain_trust_score(
        self, entity_did: str, trust_metrics: Dict[str, Any], network_context: Dict[str, Any]
    ) -> TrustExplanation:
        """
        Generate human-readable explanation of trust score

        Args:
            entity_did: DID of the entity
            trust_metrics: Trust metrics data (dict from TrustMetrics model)
            network_context: Network statistics for comparison

        Returns:
            TrustExplanation with detailed breakdown
        """
        try:
            logger.info(f"Explaining trust score for {entity_did}")
            result = await self.client.ExplainTrustScore(
                entity_did=entity_did,
                trust_metrics=json.dumps(trust_metrics),
                network_context=json.dumps(network_context),
            )
            logger.info(f"Generated trust explanation (score={result.overall_trust_score})")
            return result
        except Exception as e:
            logger.error(f"Trust explanation failed: {e}")
            raise

    async def explain_conviction_score(
        self, relationship_uri: str, conviction_data: Dict[str, Any], attestations: List[Dict[str, Any]]
    ) -> ConvictionExplanation:
        """
        Explain conviction score for a relationship

        Args:
            relationship_uri: AT URI of the relationship
            conviction_data: Conviction calculation data
            attestations: List of attestations

        Returns:
            ConvictionExplanation with detailed reasoning
        """
        try:
            logger.info(f"Explaining conviction for {relationship_uri}")
            result = await self.client.ExplainConvictionScore(
                relationship_uri=relationship_uri,
                conviction_data=json.dumps(conviction_data),
                attestations=json.dumps(attestations),
            )
            logger.info(f"Generated conviction explanation (score={result.conviction_score})")
            return result
        except Exception as e:
            logger.error(f"Conviction explanation failed: {e}")
            raise

    async def explain_path_choice(
        self,
        from_did: str,
        to_did: str,
        chosen_path: Dict[str, Any],
        alternative_paths: List[Dict[str, Any]],
        selection_criteria: str,
    ) -> PathExplanation:
        """
        Explain why a particular introduction path was chosen

        Args:
            from_did: Starting entity DID
            to_did: Target entity DID
            chosen_path: The selected path data
            alternative_paths: Other paths that were considered
            selection_criteria: Criteria used for selection

        Returns:
            PathExplanation with reasoning
        """
        try:
            logger.info(f"Explaining path choice: {from_did} → {to_did}")
            result = await self.client.ExplainPathChoice(
                from_did=from_did,
                to_did=to_did,
                chosen_path=json.dumps(chosen_path),
                alternative_paths=json.dumps(alternative_paths),
                selection_criteria=selection_criteria,
            )
            logger.info(f"Generated path explanation (hops={result.hop_count})")
            return result
        except Exception as e:
            logger.error(f"Path explanation failed: {e}")
            raise

    # ==========================================
    # Introduction Orchestration
    # ==========================================

    async def generate_intro_request(
        self,
        requester_did: str,
        requester_context: str,
        intermediary_did: str,
        intermediary_context: str,
        target_did: str,
        target_context: str,
        introduction_purpose: str,
        relationship_data: Dict[str, Any],
    ) -> IntroductionMessage:
        """
        Generate personalized introduction request message

        Args:
            requester_did: DID of person requesting intro
            requester_context: Context about requester
            intermediary_did: DID of person making intro
            intermediary_context: Context about intermediary
            target_did: DID of target person
            target_context: Context about target
            introduction_purpose: Why this intro matters
            relationship_data: Relationship strengths and context

        Returns:
            IntroductionMessage with personalized content
        """
        try:
            logger.info(f"Generating intro request: {requester_did} → {intermediary_did} → {target_did}")
            result = await self.client.GenerateIntroRequest(
                requester_did=requester_did,
                requester_context=requester_context,
                intermediary_did=intermediary_did,
                intermediary_context=intermediary_context,
                target_did=target_did,
                target_context=target_context,
                introduction_purpose=introduction_purpose,
                relationship_data=json.dumps(relationship_data),
            )
            logger.info(f"Generated intro message (success_prob={result.success_probability}%)")
            return result
        except Exception as e:
            logger.error(f"Intro request generation failed: {e}")
            raise

    async def generate_forwarding_intro(
        self,
        requester_context: str,
        target_context: str,
        intermediary_relationships: str,
        introduction_purpose: str,
        requested_outcome: str,
    ) -> ForwardingIntro:
        """
        Generate forwarding introduction text for intermediary

        Args:
            requester_context: Context about requester
            target_context: Context about target
            intermediary_relationships: How intermediary knows both parties
            introduction_purpose: Why this intro matters
            requested_outcome: Desired outcome (meeting, email, advice, etc.)

        Returns:
            ForwardingIntro with text to forward
        """
        try:
            logger.info(f"Generating forwarding intro (outcome={requested_outcome})")
            result = await self.client.GenerateForwardingIntro(
                requester_context=requester_context,
                target_context=target_context,
                intermediary_relationships=intermediary_relationships,
                introduction_purpose=introduction_purpose,
                requested_outcome=requested_outcome,
            )
            logger.info("Generated forwarding intro text")
            return result
        except Exception as e:
            logger.error(f"Forwarding intro generation failed: {e}")
            raise

    async def generate_followup(
        self, original_message: str, days_since_sent: int, any_responses: bool, new_context: Optional[str] = None
    ) -> FollowupMessage:
        """
        Generate appropriate followup message

        Args:
            original_message: The original message sent
            days_since_sent: Days since original was sent
            any_responses: Whether any responses were received
            new_context: New information to mention

        Returns:
            FollowupMessage with followup content
        """
        try:
            logger.info(f"Generating followup ({days_since_sent} days later, responses={any_responses})")
            result = await self.client.GenerateFollowup(
                original_message=original_message,
                days_since_sent=days_since_sent,
                any_responses=any_responses,
                new_context=new_context,
            )
            logger.info("Generated followup message")
            return result
        except Exception as e:
            logger.error(f"Followup generation failed: {e}")
            raise

    async def plan_intro_orchestration(
        self,
        requester_did: str,
        target_did: str,
        intro_path: List[str],
        relationship_data: Dict[str, Any],
        introduction_purpose: str,
    ) -> IntroOrchestrationPlan:
        """
        Plan multi-step introduction orchestration

        Args:
            requester_did: DID of requester
            target_did: DID of target
            intro_path: List of DIDs in the introduction path
            relationship_data: Trust scores and context for each hop
            introduction_purpose: Why this intro matters

        Returns:
            IntroOrchestrationPlan with step-by-step plan
        """
        try:
            logger.info(f"Planning orchestration: {requester_did} → {target_did} ({len(intro_path)} hops)")
            result = await self.client.PlanIntroductionOrchestration(
                requester_did=requester_did,
                target_did=target_did,
                intro_path=json.dumps(intro_path),
                relationship_data=json.dumps(relationship_data),
                introduction_purpose=introduction_purpose,
            )
            logger.info(f"Generated {result.total_steps}-step orchestration plan (success_prob={result.success_probability}%)")
            return result
        except Exception as e:
            logger.error(f"Orchestration planning failed: {e}")
            raise

    async def assess_intro_feasibility(
        self,
        requester_did: str,
        target_did: str,
        proposed_path: Dict[str, Any],
        relationship_data: Dict[str, Any],
        introduction_purpose: str,
        timing_context: Optional[str] = None,
    ) -> IntroFeasibility:
        """
        Assess feasibility of introduction before attempting

        Args:
            requester_did: DID of requester
            target_did: DID of target
            proposed_path: Proposed introduction path
            relationship_data: Relationship strengths and context
            introduction_purpose: Why this intro matters
            timing_context: Any timing considerations

        Returns:
            IntroFeasibility with assessment
        """
        try:
            logger.info(f"Assessing intro feasibility: {requester_did} → {target_did}")
            result = await self.client.AssessIntroductionFeasibility(
                requester_did=requester_did,
                target_did=target_did,
                proposed_path=json.dumps(proposed_path),
                relationship_data=json.dumps(relationship_data),
                introduction_purpose=introduction_purpose,
                timing_context=timing_context,
            )
            logger.info(f"Feasibility: {result.feasibility_level} (score={result.feasibility_score}/100)")
            return result
        except Exception as e:
            logger.error(f"Feasibility assessment failed: {e}")
            raise


# Singleton instance
_protocol_agent_service: Optional[ProtocolAgentService] = None


def get_protocol_agent_service() -> ProtocolAgentService:
    """
    Get singleton instance of ProtocolAgentService

    Returns:
        ProtocolAgentService instance
    """
    global _protocol_agent_service
    if _protocol_agent_service is None:
        _protocol_agent_service = ProtocolAgentService()
    return _protocol_agent_service

