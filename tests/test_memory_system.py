import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.task.parser import TaskParser
from backend.memory.store import MemoryStore
from backend.memory.retriever import MemoryRetriever
from backend.memory.extractor import MemoryExtractor
from backend.memory.models import MemoryItem, MemoryType, LifecycleStatus, RelationshipMemory
from backend.orchestration.controller import Write4UContextController
from backend.models.schemas import ContextItem

client = TestClient(app)

def test_memory_store_buckets():
    store = MemoryStore(storage_path=":memory:")
    memories = store.get_all_memories()
    assert len(memories) >= 5

    # Check factual memory
    fieldchain_fact = [m for m in memories if m.subject == "FieldChain"]
    assert len(fieldchain_fact) == 1
    assert fieldchain_fact[0].type == MemoryType.FACTUAL
    assert fieldchain_fact[0].confidence >= 0.95
    assert len(fieldchain_fact[0].sources) >= 1
    assert fieldchain_fact[0].lifecycle_status == LifecycleStatus.ACTIVE

    # Check relationship memory
    prof_vance = store.get_relationship("Prof. Xavier Vance")
    assert prof_vance is not None
    assert prof_vance.organization == "MIT CSAIL"
    assert "FieldChain" in prof_vance.associated_projects
    assert prof_vance.preferred_communication_style == "formal_academic"

def test_memory_retriever_grounding():
    retriever = MemoryRetriever()
    task = TaskParser.parse("Write a follow-up to Prof. Xavier Vance about our FieldChain research.")

    retrieved = retriever.retrieve_for_task(task)
    assert retrieved["relationship"] is not None
    assert retrieved["relationship"].entity_name == "Prof. Xavier Vance"
    assert len(retrieved["facts"]) >= 1
    assert len(retrieved["context_items"]) >= 1

    # Check canonical ContextItem format
    rel_item = retrieved["context_items"][0]
    assert rel_item.source == "personal_memory"
    assert rel_item.reliability >= 0.90
    assert "MIT CSAIL" in rel_item.content

def test_memory_extractor_and_transient_filtering():
    store = MemoryStore(storage_path=":memory:")

    # Stable research fact should be extracted
    stable_item = ContextItem(
        id="gmail_999",
        source="gmail",
        type="email",
        timestamp="2026-09-20T12:00:00",
        people=["Prof. Xavier Vance"],
        entities=["FieldChain"],
        content="Our paper on Byzantine consensus limits in distributed systems was accepted for publication.",
        reliability=0.98
    )

    # Transient instruction should be rejected
    transient_item = ContextItem(
        id="gmail_998",
        source="gmail",
        type="email",
        timestamp="2026-09-20T12:00:00",
        people=["Colleague"],
        entities=["Sync"],
        content="Please review this draft asap, it is urgent by tomorrow morning.",
        reliability=0.95
    )

    extracted = MemoryExtractor.extract_from_evidence([stable_item, transient_item], store)
    assert len(extracted) == 1
    assert "Byzantine consensus" in extracted[0].fact
    assert extracted[0].lifecycle_status == LifecycleStatus.CANDIDATE
    assert extracted[0].sources == ["gmail_999"]

def test_controller_memory_integration():
    controller = Write4UContextController()
    result = controller.execute_task(
        user_prompt="Write a follow-up to Prof. Xavier Vance about FieldChain.",
        page_context={"site": "gmail"}
    )

    assert result.retrieved_memories_count > 0
    assert any(it.source == "personal_memory" for it in result.selected_items)
    assert "MIT CSAIL" in result.generated_draft or "FieldChain" in result.generated_draft

def test_memory_api_endpoint():
    res = client.get("/api/memory")
    assert res.status_code == 200
    data = res.json()
    assert "total_memories" in data
    assert "facts" in data
    assert "relationships" in data
    assert "styles" in data
    assert len(data["relationships"]) >= 2
