import re
from typing import List, Optional
from datetime import datetime
from .models import MemoryItem, MemoryType, LifecycleStatus
from .store import MemoryStore
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class MemoryExtractor:
    """
    Distills stable, recurring facts, relationships, and writing habits from verified evidence.
    Prevents transient task instructions ('urgent', 'quick update') from polluting long-term memory.
    """

    TRANSIENT_PATTERNS = [
        r"\burgent\b",
        r"\basap\b",
        r"\bby tomorrow\b",
        r"\bplease review today\b",
        r"\bdraft\b"
    ]

    @classmethod
    def is_stable_fact(cls, text: str) -> bool:
        t_lower = text.lower()
        # Reject transient phrases
        if any(re.search(pat, t_lower) for pat in cls.TRANSIENT_PATTERNS):
            return False
        # Accept stable patterns (papers, awards, affiliations, projects, roles)
        stable_markers = [
            "research", "paper", "award", "consensus", "advisor", "professor",
            "benchmark", "lab", "university", "tps", "finality", "sharding"
        ]
        return any(m in t_lower for m in stable_markers)

    @classmethod
    def extract_from_evidence(cls, evidence_items: List[ContextItem], store: MemoryStore) -> List[MemoryItem]:
        new_memories: List[MemoryItem] = []

        for item in evidence_items:
            # Check if this item reveals a stable fact
            first_sentence = item.content.split("\n")[0].strip()
            if len(first_sentence) > 20 and cls.is_stable_fact(first_sentence):
                # Check for existing duplicate in store
                existing = [m for m in store.get_all_memories() if m.fact.lower() == first_sentence.lower()]
                if not existing:
                    subject = item.entities[0] if item.entities else (item.people[0] if item.people else item.source)
                    mem = MemoryItem(
                        memory_id=f"mem_ext_{len(store.get_all_memories()) + len(new_memories) + 1}",
                        type=MemoryType.FACTUAL,
                        subject=subject,
                        fact=first_sentence,
                        confidence=min(0.95, item.reliability),
                        sources=[item.id],
                        lifecycle_status=LifecycleStatus.CANDIDATE
                    )
                    new_memories.append(mem)
                    store.add_memory(mem)

        return new_memories
