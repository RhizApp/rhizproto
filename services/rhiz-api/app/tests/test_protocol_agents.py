"""
Tests for Protocol Agent Services

Testing AI-powered protocol features with BAML
"""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.protocol_agents import ProtocolAgentService, get_protocol_agent_service


@pytest.fixture
def agent_service():
    """Create protocol agent service instance"""
    return ProtocolAgentService()


@pytest.fixture
def mock_baml_client():
    """Mock BAML client for testing"""
    with patch("app.services.protocol_agents.b") as mock_client:
        yield mock_client


class TestRelationshipExtraction:
    """Tests for relationship extraction"""

    @pytest.mark.asyncio
    async def test_extract_relationships_from_text(self, agent_service, mock_baml_client):
        """Test extracting relationships from text"""
        # Arrange
        text = "Alice and Bob co-founded TechCo in 2020 and worked together for 3 years"

        mock_result = MagicMock()
        mock_result.total_found = 1
        mock_result.extraction_quality = 85
        mock_result.ambiguous_cases = []

        mock_relationship = MagicMock()
        mock_relationship.participant_a_name = "Alice"
        mock_relationship.participant_b_name = "Bob"
        mock_relationship.relationship_type = "professional"
        mock_relationship.relationship_strength = 85
        mock_relationship.context = "Co-founded TechCo, worked together 3 years"
        mock_relationship.confidence_score = 90

        mock_result.relationships = [mock_relationship]

        mock_baml_client.ExtractRelationshipsFromText = AsyncMock(return_value=mock_result)

        # Act
        result = await agent_service.extract_relationships_from_text(text)

        # Assert
        assert result.total_found == 1
        assert result.extraction_quality == 85
        assert len(result.relationships) == 1
        assert result.relationships[0].participant_a_name == "Alice"
        assert result.relationships[0].participant_b_name == "Bob"
        assert result.relationships[0].relationship_strength == 85

        mock_baml_client.ExtractRelationshipsFromText.assert_called_once_with(
            text=text, context_hint=None
        )

    @pytest.mark.asyncio
    async def test_extract_relationships_with_context(self, agent_service, mock_baml_client):
        """Test extraction with context hint"""
        # Arrange
        text = "They worked on the product launch together"
        context = "Tech startup founders"

        mock_result = MagicMock()
        mock_result.total_found = 1
        mock_result.extraction_quality = 75
        mock_result.ambiguous_cases = []
        mock_result.relationships = []

        mock_baml_client.ExtractRelationshipsFromText = AsyncMock(return_value=mock_result)

        # Act
        result = await agent_service.extract_relationships_from_text(text, context)

        # Assert
        mock_baml_client.ExtractRelationshipsFromText.assert_called_once_with(
            text=text, context_hint=context
        )

    @pytest.mark.asyncio
    async def test_assess_relationship_quality(self, agent_service, mock_baml_client):
        """Test relationship quality assessment"""
        # Arrange
        context = "Co-founded TechCo in 2020, worked together for 3 years, raised $5M Series A"
        strength = 85

        mock_result = MagicMock()
        mock_result.has_sufficient_context = True
        mock_result.has_quantifiable_metrics = True
        mock_result.has_verification_potential = True
        mock_result.quality_score = 90
        mock_result.attestation_potential = 85
        mock_result.strength_justification = "Strong professional relationship with clear metrics"
        mock_result.suggested_improvements = []

        mock_baml_client.AssessRelationshipQuality = AsyncMock(return_value=mock_result)

        # Act
        result = await agent_service.assess_relationship_quality(context, strength)

        # Assert
        assert result.quality_score == 90
        assert result.has_sufficient_context is True
        assert result.has_quantifiable_metrics is True

        mock_baml_client.AssessRelationshipQuality.assert_called_once_with(
            relationship_context=context, claimed_strength=strength
        )


class TestTrustExplanations:
    """Tests for trust score explanations"""

    @pytest.mark.asyncio
    async def test_explain_trust_score(self, agent_service, mock_baml_client):
        """Test trust score explanation"""
        # Arrange
        entity_did = "did:plc:alice123"
        trust_metrics = {
            "trustScore": 88,
            "reputation": 91,
            "reciprocity": 85,
            "consistency": 89,
        }
        network_context = {"averageTrustScore": 75, "medianTrustScore": 72}

        mock_result = MagicMock()
        mock_result.overall_trust_score = 88
        mock_result.explanation_summary = "High trust based on strong network reputation"
        mock_result.breakdown = []
        mock_result.strengths = ["Strong reputation", "Consistent behavior"]
        mock_result.concerns = []
        mock_result.comparison_to_network = "Above average"
        mock_result.trend = "stable"
        mock_result.recommendation = "Highly trustworthy entity"

        mock_baml_client.ExplainTrustScore = AsyncMock(return_value=mock_result)

        # Act
        result = await agent_service.explain_trust_score(
            entity_did, trust_metrics, network_context
        )

        # Assert
        assert result.overall_trust_score == 88
        assert "reputation" in result.explanation_summary.lower()
        assert len(result.strengths) > 0

        mock_baml_client.ExplainTrustScore.assert_called_once()

    @pytest.mark.asyncio
    async def test_explain_conviction_score(self, agent_service, mock_baml_client):
        """Test conviction score explanation"""
        # Arrange
        relationship_uri = "at://did:plc:alice/net.rhiz.relationship.record/abc123"
        conviction_data = {"score": 85, "attestationCount": 5}
        attestations = [{"attester": "did:plc:carol", "type": "verify", "confidence": 90}]

        mock_result = MagicMock()
        mock_result.conviction_score = 85
        mock_result.confidence_level = "high"
        mock_result.attestation_summary = "5 attestations, mostly positive"
        mock_result.key_attesters = ["did:plc:carol"]
        mock_result.positive_signals = ["High-reputation attesters"]
        mock_result.negative_signals = []
        mock_result.recommendation = "Strong network confidence"
        mock_result.verification_status = "strong"

        mock_baml_client.ExplainConvictionScore = AsyncMock(return_value=mock_result)

        # Act
        result = await agent_service.explain_conviction_score(
            relationship_uri, conviction_data, attestations
        )

        # Assert
        assert result.conviction_score == 85
        assert result.confidence_level == "high"
        assert len(result.key_attesters) > 0


class TestIntroductionOrchestration:
    """Tests for introduction orchestration"""

    @pytest.mark.asyncio
    async def test_generate_intro_request(self, agent_service, mock_baml_client):
        """Test generating introduction request"""
        # Arrange
        mock_result = MagicMock()
        mock_result.recipient_did = "did:plc:intermediary"
        mock_result.recipient_name = "Carol"
        mock_result.subject_line = "Introduction request: Alice → Bob"
        mock_result.message_body = "Hi Carol, would you be willing to introduce me to Bob?"
        mock_result.message_tone = MagicMock()
        mock_result.message_tone.formality = "professional"
        mock_result.context_highlights = []
        mock_result.call_to_action = "Let me know if you're comfortable making this intro"
        mock_result.optimal_send_time = "2025-10-24T10:00:00Z"
        mock_result.followup_timing_days = 5
        mock_result.success_probability = 75
        mock_result.personalization_score = 85

        mock_baml_client.GenerateIntroRequest = AsyncMock(return_value=mock_result)

        # Act
        result = await agent_service.generate_intro_request(
            requester_did="did:plc:alice",
            requester_context="Founder of TechCo",
            intermediary_did="did:plc:carol",
            intermediary_context="Former colleague",
            target_did="did:plc:bob",
            target_context="Investor at VC Fund",
            introduction_purpose="Seeking Series A investment",
            relationship_data={"alice_carol": 85, "carol_bob": 78},
        )

        # Assert
        assert result.recipient_name == "Carol"
        assert result.success_probability == 75
        assert "Introduction" in result.subject_line

    @pytest.mark.asyncio
    async def test_plan_intro_orchestration(self, agent_service, mock_baml_client):
        """Test planning introduction orchestration"""
        # Arrange
        mock_result = MagicMock()
        mock_result.total_steps = 3
        mock_result.steps = []
        mock_result.timeline_days = 14
        mock_result.success_probability = 65
        mock_result.risk_factors = ["Two hops required"]
        mock_result.mitigation_strategies = ["Strengthen intermediary relationship first"]
        mock_result.alternative_paths = []

        mock_baml_client.PlanIntroductionOrchestration = AsyncMock(return_value=mock_result)

        # Act
        result = await agent_service.plan_intro_orchestration(
            requester_did="did:plc:alice",
            target_did="did:plc:bob",
            intro_path=["did:plc:alice", "did:plc:carol", "did:plc:bob"],
            relationship_data={"hops": [{"strength": 85}, {"strength": 78}]},
            introduction_purpose="Professional networking",
        )

        # Assert
        assert result.total_steps == 3
        assert result.timeline_days == 14
        assert result.success_probability == 65
        assert len(result.risk_factors) > 0

    @pytest.mark.asyncio
    async def test_assess_intro_feasibility(self, agent_service, mock_baml_client):
        """Test assessing introduction feasibility"""
        # Arrange
        mock_result = MagicMock()
        mock_result.feasibility_score = 75
        mock_result.feasibility_level = "high"
        mock_result.success_factors = ["Strong relationships", "Clear value proposition"]
        mock_result.blocking_factors = []
        mock_result.recommended_approach = "Direct introduction request"
        mock_result.timing_recommendation = "now"
        mock_result.alternative_suggestions = []

        mock_baml_client.AssessIntroductionFeasibility = AsyncMock(return_value=mock_result)

        # Act
        result = await agent_service.assess_intro_feasibility(
            requester_did="did:plc:alice",
            target_did="did:plc:bob",
            proposed_path={"hops": 2, "strength": 80},
            relationship_data={"alice_carol": 85, "carol_bob": 78},
            introduction_purpose="Professional collaboration",
        )

        # Assert
        assert result.feasibility_score == 75
        assert result.feasibility_level == "high"
        assert result.timing_recommendation == "now"


class TestServiceSingleton:
    """Tests for service singleton"""

    def test_get_protocol_agent_service_singleton(self):
        """Test that service is a singleton"""
        # Act
        service1 = get_protocol_agent_service()
        service2 = get_protocol_agent_service()

        # Assert
        assert service1 is service2


class TestErrorHandling:
    """Tests for error handling"""

    @pytest.mark.asyncio
    async def test_extraction_error_handling(self, agent_service, mock_baml_client):
        """Test error handling in extraction"""
        # Arrange
        mock_baml_client.ExtractRelationshipsFromText = AsyncMock(
            side_effect=Exception("API error")
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await agent_service.extract_relationships_from_text("test text")

        assert "API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_orchestration_error_handling(self, agent_service, mock_baml_client):
        """Test error handling in orchestration"""
        # Arrange
        mock_baml_client.GenerateIntroRequest = AsyncMock(
            side_effect=Exception("Generation failed")
        )

        # Act & Assert
        with pytest.raises(Exception):
            await agent_service.generate_intro_request(
                requester_did="did:plc:alice",
                requester_context="context",
                intermediary_did="did:plc:carol",
                intermediary_context="context",
                target_did="did:plc:bob",
                target_context="context",
                introduction_purpose="purpose",
                relationship_data={},
            )

