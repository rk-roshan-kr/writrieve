import pytest
from backend.task.parser import TaskParser
from backend.evidence.state import EvidenceState, TerminalStatus
from backend.writing.profiles.style_profile import PersonalWritingProfile
from backend.writing.profiles.exemplars import ExemplarStore
from backend.writing.blueprints.email_blueprint import EmailBlueprintBuilder
from backend.writing.blueprints.linkedin_blueprint import LinkedInBlueprintBuilder
from backend.writing.engine import WritingTaskEngine
from backend.models.schemas import ContextItem

def test_writing_style_profile_and_exemplars():
    profile = PersonalWritingProfile()
    assert profile.email.formality == 0.72
    assert profile.linkedin.hard_char_limit == 3000

    email_ex = ExemplarStore.get_exemplars("email")
    assert len(email_ex) >= 1
    assert "Dear Professor" in email_ex[0].sample_text

    linkedin_ex = ExemplarStore.get_exemplars("linkedin")
    assert len(linkedin_ex) >= 1
    assert "#" in linkedin_ex[0].sample_text

def test_email_blueprint_builder():
    task = TaskParser.parse("Write a follow-up to Prof. Xavier Vance about our FieldChain research.")
    evidence = EvidenceState(
        items=[
            ContextItem(
                id="item_01",
                source="gmail",
                type="email",
                timestamp="2026-09-18T10:00:00",
                people=["Prof. Xavier Vance"],
                entities=["FieldChain"],
                content="FieldChain consensus achieved 19.4k TPS across 128 nodes.",
                reliability=0.98
            )
        ]
    )
    profile = PersonalWritingProfile()
    bp = EmailBlueprintBuilder.build(task, evidence, profile)

    assert bp.medium == "email"
    assert "greeting" in bp.structure_sequence
    assert "proposed_next_step" in bp.structure_sequence
    assert len(bp.must_include_facts) >= 1
    prompt = bp.render_instruction_prompt()
    assert "WRITING BLUEPRINT" in prompt

def test_linkedin_blueprint_builder():
    task = TaskParser.parse("Write a LinkedIn post announcing our CCNCPS award.")
    evidence = EvidenceState(
        items=[
            ContextItem(
                id="item_02",
                source="calendar",
                type="event",
                timestamp="2026-09-16T10:00:00",
                people=["Prof. Xavier Vance"],
                entities=["CCNCPS"],
                content="Best Poster Runner-Up in Distributed Systems at CCNCPS 2026.",
                reliability=0.95
            )
        ]
    )
    profile = PersonalWritingProfile()
    bp = LinkedInBlueprintBuilder.build(task, evidence, profile)

    assert bp.medium == "linkedin"
    assert bp.max_characters == 3000
    assert "declarative_hook" in bp.structure_sequence
    assert "hashtags" in bp.structure_sequence

def test_writing_task_engine_execution_and_multipass_verification():
    from backend.connectors.mock_provider import MockContextProvider
    provider = MockContextProvider()
    items = provider.get_all_candidates()[:10]

    engine = WritingTaskEngine()
    task = TaskParser.parse("Write a follow-up to Prof. Xavier Vance about FieldChain.")
    evidence = EvidenceState(
        terminal_status=TerminalStatus.SUCCESS,
        items=items
    )

    result = engine.execute_writing(task, evidence)

    assert result.blueprint.medium == "email"
    assert len(result.final_draft) > 50
    assert result.verification.pass_1_platform is True
    assert result.verification.factual_report.grounding_ratio >= 0.8
    assert len(result.verification.factual_report.claims) > 0
