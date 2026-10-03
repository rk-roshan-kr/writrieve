from backend.planner.laya_decision import LayaDecisionEngine

def test_laya_source_gating():
    laya = LayaDecisionEngine()
    
    # 1. Academic follow-up prompt
    sources = ["gmail", "calendar", "drive", "contacts", "linkedin"]
    probs = laya.decide_sources("academic_email_followup", "Write a follow-up email to the professor I met at the conference about continuing our research.", sources)
    
    # Gmail and Calendar should have high probabilities (>0.80)
    assert probs["gmail"] >= 0.85
    assert probs["calendar"] >= 0.80
    assert probs["drive"] >= 0.65
    # LinkedIn should have low probability (<0.30)
    assert probs["linkedin"] < 0.30

def test_laya_sufficiency_feedback_loop():
    laya = LayaDecisionEngine()

    # Incomplete evidence (only 1 item out of 5 requirements)
    res_incomplete = laya.evaluate_sufficiency_gate(
        retrieved_evidence_count=1,
        covered_requirements=1,
        total_requirements=5,
        max_evidence_needed=9
    )
    assert res_incomplete.decision == "RETRIEVE_AGAIN"
    assert res_incomplete.probabilities["NEED_MORE"] > 0.50

    # Sufficient evidence (9 items covering all 5 requirements)
    res_sufficient = laya.evaluate_sufficiency_gate(
        retrieved_evidence_count=9,
        covered_requirements=5,
        total_requirements=5,
        max_evidence_needed=9
    )
    assert res_sufficient.decision == "SUFFICIENT_GENERATE"
    assert res_sufficient.confidence >= 0.80
    assert res_sufficient.latency_ms < 5.0 # Sub-5ms decision latency

def test_laya_conflict_detection():
    laya = LayaDecisionEngine()
    
    class MockEvidence:
        def __init__(self, source, content):
            self.source = source
            self.content = content

    items = [
        MockEvidence("calendar", "Coffee chat on September 16 at CCNCPS"),
        MockEvidence("gmail", "Follow-up email on September 18 regarding FieldChain")
    ]

    conflicts = laya.detect_conflicts(items)
    assert len(conflicts) > 0
    assert conflicts[0]["status"] == "verified_sequence"
