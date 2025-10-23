"""
Tests for Agent API Endpoints

Testing REST API for protocol-level AI features
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_agent_service():
    """Mock protocol agent service"""
    with patch("app.api.agents.get_protocol_agent_service") as mock_get:
        mock_service = MagicMock()
        mock_get.return_value = mock_service
        yield mock_service


class TestRelationshipExtractionAPI:
    """Tests for relationship extraction endpoints"""

    def test_extract_relationships(self, mock_agent_service):
        """Test POST /api/v1/agents/relationships/extract"""
        # Arrange
        mock_result = MagicMock()
        mock_result.relationships = []
        mock_result.total_found = 1
        mock_result.extraction_quality = 85
        mock_result.ambiguous_cases = []

        mock_agent_service.extract_relationships_from_text = AsyncMock(return_value=mock_result)

        # Act
        response = client.post(
            "/api/v1/agents/relationships/extract",
            json={
                "text": "Alice and Bob co-founded TechCo",
                "context_hint": None
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_found"] == 1
        assert data["extraction_quality"] == 85

    def test_extract_relationships_with_context(self, mock_agent_service):
        """Test extraction with context hint"""
        # Arrange
        mock_result = MagicMock()
        mock_result.relationships = []
        mock_result.total_found = 0
        mock_result.extraction_quality = 70
        mock_result.ambiguous_cases = []

        mock_agent_service.extract_relationships_from_text = AsyncMock(return_value=mock_result)

        # Act
        response = client.post(
            "/api/v1/agents/relationships/extract",
            json={
                "text": "They worked together",
                "context_hint": "Tech startup founders"
            }
        )

        # Assert
        assert response.status_code == 200

    def test_assess_relationship_quality(self, mock_agent_service):
        """Test POST /api/v1/agents/relationships/assess-quality"""
        # Arrange
        mock_result = MagicMock()
        mock_result.has_sufficient_context = True
        mock_result.has_quantifiable_metrics = True
        mock_result.has_verification_potential = True
        mock_result.strength_justification = "Strong evidence"
        mock_result.suggested_improvements = []
        mock_result.quality_score = 90
        mock_result.attestation_potential = 85

        mock_agent_service.assess_relationship_quality = AsyncMock(return_value=mock_result)

        # Act
        response = client.post(
            "/api/v1/agents/relationships/assess-quality",
            json={
                "relationship_context": "Co-founded company, worked together 3 years",
                "claimed_strength": 85
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["quality_score"] == 90
        assert data["has_sufficient_context"] is True


class TestTrustExplanationAPI:
    """Tests for trust explanation endpoints"""

    def test_explain_trust_score(self, mock_agent_service):
        """Test POST /api/v1/agents/trust/explain"""
        # Arrange
        mock_result = MagicMock()
        mock_result.overall_trust_score = 88
        mock_result.explanation_summary = "High trust"
        mock_result.breakdown = []
        mock_result.strengths = ["Strong reputation"]
        mock_result.concerns = []
        mock_result.comparison_to_network = "Above average"
        mock_result.trend = "stable"
        mock_result.recommendation = "Highly trustworthy"

        mock_agent_service.explain_trust_score = AsyncMock(return_value=mock_result)

        # Act
        response = client.post(
            "/api/v1/agents/trust/explain",
            json={
                "entity_did": "did:plc:alice",
                "trust_metrics": {"trustScore": 88},
                "network_context": {"average": 75}
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["overall_trust_score"] == 88
        assert len(data["strengths"]) > 0

    def test_explain_conviction_score(self, mock_agent_service):
        """Test POST /api/v1/agents/trust/explain-conviction"""
        # Arrange
        mock_result = MagicMock()
        mock_result.conviction_score = 85
        mock_result.confidence_level = "high"
        mock_result.attestation_summary = "Strong attestations"
        mock_result.key_attesters = ["did:plc:carol"]
        mock_result.positive_signals = ["High reputation"]
        mock_result.negative_signals = []
        mock_result.recommendation = "Trust this relationship"
        mock_result.verification_status = "strong"

        mock_agent_service.explain_conviction_score = AsyncMock(return_value=mock_result)

        # Act
        response = client.post(
            "/api/v1/agents/trust/explain-conviction",
            json={
                "relationship_uri": "at://did:plc:alice/net.rhiz.relationship.record/abc",
                "conviction_data": {"score": 85},
                "attestations": []
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["conviction_score"] == 85
        assert data["confidence_level"] == "high"

    def test_explain_path_choice(self, mock_agent_service):
        """Test POST /api/v1/agents/trust/explain-path"""
        # Arrange
        mock_result = MagicMock()
        mock_result.path_strength = 80
        mock_result.hop_count = 2
        mock_result.why_optimal = "Best balance of strength and hops"
        mock_result.relationship_quality = ["Strong", "Strong"]
        mock_result.alternative_paths_considered = 3
        mock_result.why_others_rejected = "Weaker relationships"
        mock_result.risk_factors = []
        mock_result.success_probability = 75
        mock_result.strategy_recommendation = "Proceed with intro"

        mock_agent_service.explain_path_choice = AsyncMock(return_value=mock_result)

        # Act
        response = client.post(
            "/api/v1/agents/trust/explain-path",
            json={
                "from_did": "did:plc:alice",
                "to_did": "did:plc:bob",
                "chosen_path": {"hops": 2},
                "alternative_paths": [],
                "selection_criteria": "maximize_strength"
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["hop_count"] == 2
        assert data["success_probability"] == 75


class TestIntroductionOrchestrationAPI:
    """Tests for introduction orchestration endpoints"""

    def test_generate_intro_request(self, mock_agent_service):
        """Test POST /api/v1/agents/intros/generate-request"""
        # Arrange
        mock_tone = MagicMock()
        mock_tone.formality = "professional"
        mock_tone.urgency = "medium"
        mock_tone.length = "moderate"
        mock_tone.model_dump = MagicMock(return_value={
            "formality": "professional",
            "urgency": "medium",
            "length": "moderate"
        })

        mock_result = MagicMock()
        mock_result.recipient_did = "did:plc:carol"
        mock_result.recipient_name = "Carol"
        mock_result.subject_line = "Intro request"
        mock_result.message_body = "Message body"
        mock_result.message_tone = mock_tone
        mock_result.context_highlights = []
        mock_result.call_to_action = "Let me know"
        mock_result.optimal_send_time = "2025-10-24T10:00:00Z"
        mock_result.followup_timing_days = 5
        mock_result.success_probability = 75
        mock_result.personalization_score = 85

        mock_agent_service.generate_intro_request = AsyncMock(return_value=mock_result)

        # Act
        response = client.post(
            "/api/v1/agents/intros/generate-request",
            json={
                "requester_did": "did:plc:alice",
                "requester_context": "Founder",
                "intermediary_did": "did:plc:carol",
                "intermediary_context": "Colleague",
                "target_did": "did:plc:bob",
                "target_context": "Investor",
                "introduction_purpose": "Networking",
                "relationship_data": {}
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["recipient_name"] == "Carol"
        assert data["success_probability"] == 75

    def test_plan_intro_orchestration(self, mock_agent_service):
        """Test POST /api/v1/agents/intros/plan-orchestration"""
        # Arrange
        mock_result = MagicMock()
        mock_result.total_steps = 3
        mock_result.steps = []
        mock_result.timeline_days = 14
        mock_result.success_probability = 65
        mock_result.risk_factors = ["Multiple hops"]
        mock_result.mitigation_strategies = ["Build rapport first"]
        mock_result.alternative_paths = []

        mock_agent_service.plan_intro_orchestration = AsyncMock(return_value=mock_result)

        # Act
        response = client.post(
            "/api/v1/agents/intros/plan-orchestration",
            json={
                "requester_did": "did:plc:alice",
                "target_did": "did:plc:bob",
                "intro_path": ["did:plc:alice", "did:plc:carol", "did:plc:bob"],
                "relationship_data": {},
                "introduction_purpose": "Networking"
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_steps"] == 3
        assert data["timeline_days"] == 14

    def test_assess_intro_feasibility(self, mock_agent_service):
        """Test POST /api/v1/agents/intros/assess-feasibility"""
        # Arrange
        mock_result = MagicMock()
        mock_result.feasibility_score = 75
        mock_result.feasibility_level = "high"
        mock_result.success_factors = ["Strong relationships"]
        mock_result.blocking_factors = []
        mock_result.recommended_approach = "Direct request"
        mock_result.timing_recommendation = "now"
        mock_result.alternative_suggestions = []

        mock_agent_service.assess_intro_feasibility = AsyncMock(return_value=mock_result)

        # Act
        response = client.post(
            "/api/v1/agents/intros/assess-feasibility",
            json={
                "requester_did": "did:plc:alice",
                "target_did": "did:plc:bob",
                "proposed_path": {},
                "relationship_data": {},
                "introduction_purpose": "Networking",
                "timing_context": None
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["feasibility_score"] == 75
        assert data["feasibility_level"] == "high"


class TestAPIErrorHandling:
    """Tests for API error handling"""

    def test_extraction_error_handling(self, mock_agent_service):
        """Test error handling for extraction failures"""
        # Arrange
        mock_agent_service.extract_relationships_from_text = AsyncMock(
            side_effect=Exception("Extraction failed")
        )

        # Act
        response = client.post(
            "/api/v1/agents/relationships/extract",
            json={"text": "test text"}
        )

        # Assert
        assert response.status_code == 500
        assert "failed" in response.json()["detail"].lower()

    def test_orchestration_error_handling(self, mock_agent_service):
        """Test error handling for orchestration failures"""
        # Arrange
        mock_agent_service.generate_intro_request = AsyncMock(
            side_effect=Exception("Generation failed")
        )

        # Act
        response = client.post(
            "/api/v1/agents/intros/generate-request",
            json={
                "requester_did": "did:plc:alice",
                "requester_context": "context",
                "intermediary_did": "did:plc:carol",
                "intermediary_context": "context",
                "target_did": "did:plc:bob",
                "target_context": "context",
                "introduction_purpose": "purpose",
                "relationship_data": {}
            }
        )

        # Assert
        assert response.status_code == 500


class TestInputValidation:
    """Tests for input validation"""

    def test_invalid_trust_score_range(self):
        """Test validation for claimed_strength out of range"""
        # Act
        response = client.post(
            "/api/v1/agents/relationships/assess-quality",
            json={
                "relationship_context": "Test context",
                "claimed_strength": 150  # Invalid - should be 0-100
            }
        )

        # Assert
        assert response.status_code == 422  # Validation error

    def test_missing_required_fields(self):
        """Test validation for missing required fields"""
        # Act
        response = client.post(
            "/api/v1/agents/relationships/extract",
            json={}  # Missing 'text' field
        )

        # Assert
        assert response.status_code == 422

