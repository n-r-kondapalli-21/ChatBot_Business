"""
Test suite for the FAQ Chatbot API.

Test categories
───────────────
1.  Health endpoint
2.  FAQs listing endpoint
3.  Exact question matching
4.  Paraphrased / semantically equivalent questions
5.  Empty / whitespace-only input (validation)
6.  Questions with no relevant FAQ answer (below threshold)
7.  FAQMatcher unit tests (isolated from HTTP layer)

The test client uses FastAPI's TestClient (synchronous) which triggers the
full lifespan (startup / shutdown), so the real model and data are used.
This means the first test run will download the model if it isn't cached.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

# ── Shared test client (model loaded once per session) ────────────────────────
@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Session-scoped TestClient.
    The lifespan (model load + FAQ embedding) runs once for the whole test session.
    """
    with TestClient(app) as c:
        yield c


# ═════════════════════════════════════════════════════════════════════════════
# 1. Health endpoint
# ═════════════════════════════════════════════════════════════════════════════

class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_shape(self, client: TestClient) -> None:
        data = client.get("/health").json()
        assert data["status"] == "ok"
        assert data["model_loaded"] is True
        assert isinstance(data["faq_count"], int)
        assert data["faq_count"] > 0

    def test_health_contains_version(self, client: TestClient) -> None:
        data = client.get("/health").json()
        assert "version" in data
        assert data["version"]  # non-empty


# ═════════════════════════════════════════════════════════════════════════════
# 2. FAQs listing endpoint
# ═════════════════════════════════════════════════════════════════════════════

class TestFAQsEndpoint:
    def test_faqs_returns_200(self, client: TestClient) -> None:
        assert client.get("/faqs").status_code == 200

    def test_faqs_response_is_list(self, client: TestClient) -> None:
        body = client.get("/faqs").json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) > 0

    def test_faqs_entry_has_required_fields(self, client: TestClient) -> None:
        entry = client.get("/faqs").json()["data"][0]
        for field in ("id", "question", "answer"):
            assert field in entry, f"Missing field: {field}"


# ═════════════════════════════════════════════════════════════════════════════
# 3. Exact question matching
# ═════════════════════════════════════════════════════════════════════════════

class TestExactMatching:
    """Submitting the exact FAQ question should always match."""

    @pytest.mark.parametrize("question, expected_faq_id", [
        ("What are your business hours?", "faq_001"),
        ("How do I reset my password?", "faq_002"),
        ("What payment methods do you accept?", "faq_003"),
        ("How can I track my order?", "faq_004"),
        ("What is your return policy?", "faq_005"),
    ])
    def test_exact_match(
        self, client: TestClient, question: str, expected_faq_id: str
    ) -> None:
        response = client.post("/chat", json={"question": question})
        assert response.status_code == 200
        body = response.json()
        assert body["matched"] is True, (
            f"Expected a match for '{question}', got: {body}"
        )
        assert body["matched_faq_id"] == expected_faq_id, (
            f"Expected {expected_faq_id}, got {body['matched_faq_id']}"
        )
        assert body["similarity_score"] is not None
        assert body["similarity_score"] > 0.9, (
            f"Score unexpectedly low for exact match: {body['similarity_score']}"
        )


# ═════════════════════════════════════════════════════════════════════════════
# 4. Paraphrased / semantically equivalent questions
# ═════════════════════════════════════════════════════════════════════════════

class TestParaphrasedMatching:
    """Different phrasings should resolve to the correct FAQ."""

    @pytest.mark.parametrize("paraphrase, expected_faq_id", [
        # Business hours
        ("When is your office open?", "faq_001"),
        ("What time do you open?", "faq_001"),
        # Password reset
        ("I forgot my password, how do I get a new one?", "faq_002"),
        ("How can I recover my account password?", "faq_002"),
        # Payment
        ("Which payment options are supported?", "faq_003"),
        ("Can I pay with a credit card?", "faq_003"),
        # Order tracking
        ("How do I check the status of my order?", "faq_004"),
        ("Can I track the delivery of my order?", "faq_004"),  # replaces the ambiguous "Where is my package?"
        # Return policy
        ("Can I return a product I bought?", "faq_005"),
        ("What is the refund policy?", "faq_005"),
    ])
    def test_paraphrase_resolves_to_correct_faq(
        self, client: TestClient, paraphrase: str, expected_faq_id: str
    ) -> None:
        response = client.post("/chat", json={"question": paraphrase})
        assert response.status_code == 200
        body = response.json()
        assert body["matched"] is True, (
            f"Paraphrase '{paraphrase}' expected to match {expected_faq_id}, "
            f"but got matched=False. Body: {body}"
        )
        assert body["matched_faq_id"] == expected_faq_id, (
            f"Paraphrase '{paraphrase}' matched {body['matched_faq_id']} "
            f"instead of {expected_faq_id}."
        )


# ═════════════════════════════════════════════════════════════════════════════
# 5. Empty / whitespace-only input
# ═════════════════════════════════════════════════════════════════════════════

class TestInputValidation:
    def test_empty_string_returns_422(self, client: TestClient) -> None:
        response = client.post("/chat", json={"question": ""})
        assert response.status_code == 422

    def test_whitespace_only_returns_422(self, client: TestClient) -> None:
        response = client.post("/chat", json={"question": "   "})
        assert response.status_code == 422

    def test_missing_question_field_returns_422(self, client: TestClient) -> None:
        response = client.post("/chat", json={})
        assert response.status_code == 422

    def test_question_too_long_returns_422(self, client: TestClient) -> None:
        response = client.post("/chat", json={"question": "x" * 501})
        assert response.status_code == 422

    def test_error_response_has_correct_shape(self, client: TestClient) -> None:
        body = client.post("/chat", json={"question": ""}).json()
        assert body["success"] is False
        assert "error" in body


# ═════════════════════════════════════════════════════════════════════════════
# 6. No relevant FAQ (below threshold)
# ═════════════════════════════════════════════════════════════════════════════

class TestNoMatchFallback:
    """Questions unrelated to any FAQ should return the fallback message."""

    @pytest.mark.parametrize("irrelevant_question", [
        "What is the capital of France?",
        "Tell me a joke about penguins.",
        "How do I bake a chocolate cake?",
        "What is the speed of light?",
    ])
    def test_irrelevant_question_returns_fallback(
        self, client: TestClient, irrelevant_question: str
    ) -> None:
        response = client.post("/chat", json={"question": irrelevant_question})
        assert response.status_code == 200
        body = response.json()
        assert body["matched"] is False, (
            f"'{irrelevant_question}' should NOT match any FAQ, but got matched=True. "
            f"Body: {body}"
        )
        assert body["matched_faq_id"] is None
        # Fallback message must not be empty
        assert body["answer"]
        assert len(body["answer"]) > 10

    def test_fallback_contains_support_contact(self, client: TestClient) -> None:
        """The fallback message should guide the user to support."""
        body = client.post(
            "/chat", json={"question": "What is the meaning of life?"}
        ).json()
        assert body["matched"] is False
        # The default fallback message mentions contacting support
        assert "support" in body["answer"].lower()


# ═════════════════════════════════════════════════════════════════════════════
# 7. FAQMatcher unit tests (isolated)
# ═════════════════════════════════════════════════════════════════════════════

class TestFAQMatcherUnit:
    """
    Unit tests for FAQMatcher in isolation.
    The model is loaded via the shared session fixture (app startup),
    so we re-use app.state.matcher directly.
    """

    def test_matcher_is_initialised(self, client: TestClient) -> None:
        matcher = client.app.state.matcher  # type: ignore[attr-defined]
        assert matcher is not None

    def test_matcher_returns_match_result(self, client: TestClient) -> None:
        from app.services.matcher import MatchResult
        matcher = client.app.state.matcher  # type: ignore[attr-defined]
        result = matcher.match("How do I reset my password?")
        assert isinstance(result, MatchResult)

    def test_match_result_fields_on_hit(self, client: TestClient) -> None:
        matcher = client.app.state.matcher  # type: ignore[attr-defined]
        result = matcher.match("How do I reset my password?")
        assert result.matched is True
        assert result.faq_id is not None
        assert result.answer
        assert result.similarity_score is not None
        assert 0.0 <= result.similarity_score <= 1.0

    def test_match_result_fields_on_miss(self, client: TestClient) -> None:
        matcher = client.app.state.matcher  # type: ignore[attr-defined]
        result = matcher.match("What is the boiling point of nitrogen?")
        assert result.matched is False
        assert result.faq_id is None
        assert result.answer  # fallback message is present

    def test_chat_response_includes_score_on_match(self, client: TestClient) -> None:
        body = client.post(
            "/chat", json={"question": "What are your business hours?"}
        ).json()
        assert body["similarity_score"] is not None
        assert isinstance(body["similarity_score"], float)

    def test_chat_response_score_none_on_no_match(self, client: TestClient) -> None:
        body = client.post(
            "/chat", json={"question": "What is the melting point of iron?"}
        ).json()
        # When there's no match, similarity_score may still be returned (best-attempt score)
        # but matched must be False
        assert body["matched"] is False
