from backend.planner.planner import ContextPlanner

def test_planner_academic_email():
    planner = ContextPlanner()
    intent, plan = planner.plan("Write a follow-up email to the professor I met at the conference about continuing our research.")

    assert intent.task_type == "academic_email_followup"
    assert "Prof. Xavier Vance" in (intent.recipient or intent.primary_entity)
    assert len(plan.requirements) >= 4
    assert "gmail" in plan.preferred_sources
    assert "calendar" in plan.preferred_sources
    assert "drive" in plan.preferred_sources

def test_planner_linkedin_post():
    planner = ContextPlanner()
    intent, plan = planner.plan("Write a LinkedIn post celebrating our paper presentation at CCNCPS 2026.")

    assert intent.task_type == "linkedin_post"
    assert "linkedin" in plan.preferred_sources
    assert any("conference" in r.lower() or "paper" in r.lower() for r in plan.requirements)
