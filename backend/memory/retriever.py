from typing import List, Dict, Any, Optional
from backend.task.classifier import TaskRepresentation
from .models import MemoryItem, MemoryType, RelationshipMemory, LifecycleStatus
from .store import MemoryStore
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class MemoryRetriever:
    """
    Retrieves relevant long-term memories before live connector discovery.
    Provides fast, zero-latency grounding across facts, relationships, and writing habits.
    """

    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()

    def retrieve_for_task(self, task: TaskRepresentation) -> Dict[str, Any]:
        retrieved_facts: List[MemoryItem] = []
        retrieved_styles: List[MemoryItem] = []
        relationship: Optional[RelationshipMemory] = None

        query_terms = [
            task.target_entity or "",
            task.topic or "",
            task.event_context or "",
            task.user_prompt
        ]
        q_text = " ".join([t for t in query_terms if t]).lower()

        # 1. Check Relationship Memory
        if task.target_entity:
            relationship = self.store.get_relationship(task.target_entity)

        # 2. Check Factual and Style Memories
        for mem in self.store.get_all_memories():
            if mem.lifecycle_status not in [LifecycleStatus.ACTIVE, LifecycleStatus.CONFIRMED]:
                continue

            sub_lower = mem.subject.lower()
            fact_lower = mem.fact.lower()

            # Subject or fact match
            if sub_lower in q_text or any(w in fact_lower for w in q_text.split() if len(w) > 4):
                mem.touch()
                if mem.type == MemoryType.FACTUAL:
                    retrieved_facts.append(mem)
                elif mem.type == MemoryType.WRITING_STYLE:
                    retrieved_styles.append(mem)

        # Convert to canonical ContextItem objects for immediate EvidenceState inclusion
        memory_context_items: List[ContextItem] = []

        if relationship:
            memory_context_items.append(ContextItem(
                id=f"mem_rel_{relationship.entity_name.replace(' ', '_').lower()}",
                source="personal_memory",
                type="relationship_profile",
                timestamp=relationship.last_interaction_date or "2026-09-16T12:00:00",
                people=[relationship.entity_name],
                entities=relationship.associated_projects,
                content=(
                    f"Relationship: {relationship.entity_name} ({relationship.organization})\n"
                    f"Role: {relationship.relationship_type}\n"
                    f"Projects: {', '.join(relationship.associated_projects)}\n"
                    f"Communication Style: {relationship.preferred_communication_style}\n"
                    f"Notes: {'; '.join(relationship.notes)}"
                ),
                reliability=relationship.confidence,
                provenance={"provider": "memory_store", "sources": relationship.sources}
            ))

        for f in retrieved_facts:
            memory_context_items.append(ContextItem(
                id=f.memory_id,
                source="personal_memory",
                type="factual_memory",
                timestamp=f.last_confirmed,
                people=[f.subject] if "prof" in f.subject.lower() else [],
                entities=[f.subject],
                content=f.fact,
                reliability=f.confidence,
                provenance={"provider": "memory_store", "sources": f.sources}
            ))

        return {
            "relationship": relationship,
            "facts": retrieved_facts,
            "styles": retrieved_styles,
            "context_items": memory_context_items,
            "total_memories": len(memory_context_items)
        }
