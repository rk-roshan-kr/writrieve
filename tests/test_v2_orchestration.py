import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.task.parser import TaskParser
from backend.task.classifier import TaskClass
from backend.policy.permissions import PolicyPermissions
from backend.policy.privacy import PrivacyGuard
from backend.retrieval.entity_resolution import EntityResolver
from backend.orchestration.controller import Write4UContextController
from backend.evidence.state import TerminalStatus
from backend.generation.verifier import OutputVerifier
from backend.models.schemas import ContextItem

client = TestClient(app)

def test_v2_task_parsing_and_classification():
    task_c = TaskParser.parse("Write a follow-up to Prof. Xavier Vance about our FieldChain research.")
    assert task_c.task_class == TaskClass.CLASS_C_GENERATION
    assert "Xavier Vance" in (task_c.target_entity or "")
    assert task_c.desired_tone == "professional"

    task_a = TaskParser.parse("What time is my meeting tomorrow?")
    assert task_a.task_class == TaskClass.CLASS_A_LOOKUP
    assert task_a.freshness_preference == "strict_recent"

    task_d = TaskParser.parse("Send a message to Rahul about the sync.")
    assert task_d.task_class == TaskClass.CLASS_D_AMBIGUOUS

def test_v2_entity_resolution_and_disambiguation():
    resolved_prof = EntityResolver.resolve("professor")
    assert not resolved_prof.is_ambiguous
    assert "Prof. Xavier Vance" in resolved_prof.canonical_name

    resolved_rahul = EntityResolver.resolve("rahul")
    assert resolved_rahul.is_ambiguous
    assert len(resolved_rahul.competing_candidates) >= 2

def test_v2_policy_permissions_and_privacy():
    allowed, msg = PolicyPermissions.is_action_allowed("GMAIL_LIST_MESSAGES")
    assert allowed

    forbidden, msg = PolicyPermissions.is_action_allowed("GMAIL_SEND_EMAIL")
    assert not forbidden
    assert "forbidden" in msg.lower()

    del_forbidden, _ = PolicyPermissions.is_action_allowed("GOOGLEDRIVE_DELETE_FILE")
    assert not del_forbidden

    raw_text = "Here is my secret token: api_key: secret_tok_12345678 and card 4111-2222-3333-4444"
    sanitized = PrivacyGuard.sanitize(raw_text)
    assert "4111-2222-3333-4444" not in sanitized
    assert "[REDACTED_CARD]" in sanitized

def test_v2_iterative_control_loop_and_evidence_state():
    controller = Write4UContextController()
    result = controller.execute_task(
        user_prompt="Write a follow-up to the professor I met at the conference. Mention our discussion about continuing the project, but don't sound too formal.",
        page_context={"site": "gmail"}
    )

    assert result.terminal_status == TerminalStatus.SUCCESS
    assert len(result.iteration_history) >= 1
    assert len(result.selected_items) > 0
    assert result.evidence_state.overall_sufficiency() >= 0.70
    assert result.budget_summary["exhausted"] is True or len(result.iteration_history) <= 3
    assert len(result.generated_draft) > 50

def test_v2_ambiguous_entity_triggers_ask_user():
    controller = Write4UContextController()
    result = controller.execute_task(
        user_prompt="Write an email to Rahul about the update.",
        page_context={"site": "gmail"}
    )

    assert result.terminal_status == TerminalStatus.ASK_USER
    assert "Multiple identities match" in (result.user_clarification or "")
    assert "[Execution paused" in result.generated_draft

def test_v2_output_claim_verifier():
    mock_items = [
        ContextItem(
            id="item_01",
            source="gmail",
            type="email",
            timestamp="2026-09-18T10:00:00",
            people=["Prof. Xavier Vance"],
            entities=["FieldChain"],
            content="Let's continue the FieldChain research after CCNCPS.",
            reliability=0.98
        )
    ]

    draft_with_hallucination = (
        "It was great meeting at CCNCPS regarding FieldChain. "
        "You also invited me to your lab for a fully funded PhD fellowship."
    )

    verified_text, claims = OutputVerifier.verify(draft_with_hallucination, mock_items)
    
    # The hallucinated lab tour/fellowship must be marked UNSUPPORTED
    unsupported = [c for c in claims if c.status == "UNSUPPORTED"]
    assert len(unsupported) >= 1
    assert "invited me to your lab" in unsupported[0].claim_text.lower()
    assert "invited me to your lab" not in verified_text

def test_v2_api_endpoint():
    res = client.post("/api/v2/execute", json={
        "prompt": "Write a follow-up to the professor I met at the conference about FieldChain.",
        "page_context": {"site": "gmail"}
    })
    assert res.status_code == 200
    data = res.json()
    assert "terminal_status" in data
    assert "iteration_history" in data
    assert "claims_verification" in data
    assert "budget_summary" in data
