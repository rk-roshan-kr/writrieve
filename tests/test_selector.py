from backend.context.selector import ContextSelector
from backend.planner.planner import ContextPlanner
from backend.connectors.factory import get_context_provider

def test_selector_adaptive_filtering(provider):
    planner = ContextPlanner()
    intent, plan = planner.plan("Write a follow-up email to the professor I met at the conference about continuing our research.")
    
    candidates = provider.get_all_candidates()
    assert len(candidates) == 200

    selector = ContextSelector(lambda_size_penalty=0.05, mu_redundancy=0.15)
    scored = selector.score_all_candidates(candidates, plan, intent)

    assert len(scored) == 200
    # Top item should be directly related to Xavier Vance / CCNCPS / FieldChain
    top_item = scored[0].item
    assert any("xavier" in p.lower() or "xavier" in top_item.content.lower() for p in top_item.people)

    # Distractor noise item should be penalized
    noise_items = [s for s in scored if "receipt" in s.item.content.lower() or "dental" in s.item.content.lower()]
    assert len(noise_items) > 0
    for n in noise_items:
        assert n.score_breakdown.privacy_penalty > 0.0

    # Select optimal context
    selected, funnel, reasons = selector.select_optimal_context(scored, plan, max_items=9)
    assert len(selected) <= 9
    assert funnel["candidates"] == 200
    assert funnel["selected"] == len(selected)
    assert len(reasons) >= 3
