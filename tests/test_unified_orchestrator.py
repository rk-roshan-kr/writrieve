import pytest
from backend.task.parser import TaskParser
from backend.retrieval.web_broker import WebSearchBroker
from backend.orchestration.source_router import SourceRouter
from backend.writing.evidence_packet import WritingEvidencePacket
from backend.orchestration.controller import Write4UContextController
from backend.evidence.state import TerminalStatus
from backend.models.schemas import ContextItem

def test_source_router_deconstruction():
    task = TaskParser.parse("Write a LinkedIn post about my CCNCPS experience.")
    plan = SourceRouter.plan_sources(task)

    assert plan.memory_enabled is True
    assert "web" in plan.external_sources
    assert "gmail" in plan.personal_sources
    assert len(plan.directives) >= 3

    categories = [d.source_category for d in plan.directives]
    assert "memory" in categories
    assert "web" in categories
    assert "personal" in categories

def test_web_broker_ccncps_background():
    broker = WebSearchBroker()
    results = broker.search_web("CCNCPS 2026 conference")

    assert len(results) >= 1
    ccncps_web = results[0]
    assert ccncps_web.source == "web"
    assert "Dubai" in ccncps_web.content
    assert "September 14–17, 2026" in ccncps_web.content
    assert "IEEE CCNCPS 2026" in ccncps_web.content

def test_writing_evidence_packet_compilation():
    sample_items = [
        ContextItem(
            id="web_ccncps_001",
            source="web",
            type="web_article",
            timestamp="2026-09-14T09:00:00Z",
            entities=["IEEE CCNCPS 2026", "Dubai"],
            content="Official Conference: IEEE CCNCPS 2026 held September 14-17, 2026 in Dubai.",
            reliability=0.98
        ),
        ContextItem(
            id="gmail_002",
            source="gmail",
            type="email",
            timestamp="2026-09-16T12:00:00Z",
            people=["Conference Committee"],
            entities=["FieldChain"],
            content="Congratulations on Best Poster Runner-Up in the Distributed Systems track at CCNCPS 2026.",
            reliability=0.99
        )
    ]

    packet = WritingEvidencePacket.compile("linkedin_conference_post", sample_items)
    assert len(packet.facts) == 2
    assert len(packet.external_context) >= 1
    assert len(packet.personal_experience) >= 1
    assert len(packet.forbidden_claims) >= 2
    prompt = packet.render_prompt_section()
    assert "EVIDENCE PACKET" in prompt
    assert "FORBIDDEN EXTRAPOLATIONS" in prompt

def test_end_to_end_ccncps_linkedin_post_generation():
    controller = Write4UContextController()
    result = controller.execute_task(
        user_prompt="Write a LinkedIn post about my CCNCPS experience.",
        page_context={"site": "linkedin"}
    )

    assert result.terminal_status in [TerminalStatus.SUCCESS, TerminalStatus.PARTIAL]
    assert result.writing_blueprint.medium == "linkedin"
    assert result.writing_blueprint.max_characters == 3000
    assert len(result.generated_draft) > 50

    # Verify multi-source evidence was fused
    sources_used = result.evidence_state.sources_used
    assert "personal_memory" in sources_used
    assert "web" in sources_used

    # Verify platform constraint passed
    assert result.verification_report.pass_1_platform is True
