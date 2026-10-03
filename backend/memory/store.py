import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import MemoryItem, MemoryType, LifecycleStatus, RelationshipMemory

DEFAULT_STORAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "user_memory.json")

class MemoryStore:
    """
    Persistent Long-term Memory Store for Write4U Context Engine.
    Organizes memory into three primary structured buckets:
      1. facts (Stable research / biographical claims)
      2. relationships (Entity profiles, institutions, communication styles)
      3. writing_style (Learned formatting & stylistic habits)
      (plus task memory for recent follow-up history)
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or DEFAULT_STORAGE_FILE
        self._memories: Dict[str, MemoryItem] = {}
        self._relationships: Dict[str, RelationshipMemory] = {}
        if self.storage_path == ":memory:":
            self._seed_default_memories()
        else:
            self._load_or_seed()

    def _load_or_seed(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for raw in data.get("memories", []):
                        m = MemoryItem(**raw)
                        self._memories[m.memory_id] = m
                    for raw_rel in data.get("relationships", []):
                        r = RelationshipMemory(**raw_rel)
                        self._relationships[r.entity_name.lower()] = r
                return
            except Exception as e:
                print(f"[MemoryStore] Failed to load {self.storage_path}, seeding defaults: {e}")

        self._seed_default_memories()
        self.save()

    def _seed_default_memories(self):
        # 1. Factual Memories
        default_facts = [
            MemoryItem(
                memory_id="mem_fact_001",
                type=MemoryType.FACTUAL,
                subject="FieldChain",
                fact="User conducts primary research on FieldChain: Resilient Consensus via Adaptive Sharding.",
                confidence=0.98,
                sources=["drive_001", "gmail_001"],
                lifecycle_status=LifecycleStatus.ACTIVE
            ),
            MemoryItem(
                memory_id="mem_fact_002",
                type=MemoryType.FACTUAL,
                subject="CCNCPS 2026",
                fact="User presented FieldChain poster at CCNCPS 2026 conference in San Francisco and received Best Poster Runner-Up.",
                confidence=0.99,
                sources=["gmail_002", "cal_001"],
                lifecycle_status=LifecycleStatus.ACTIVE
            ),
            MemoryItem(
                memory_id="mem_fact_003",
                type=MemoryType.FACTUAL,
                subject="TARS Project",
                fact="User's open-source distributed coordination subsystem is named TARS (Topology-Aware Routing System).",
                confidence=0.92,
                sources=["drive_003"],
                lifecycle_status=LifecycleStatus.ACTIVE
            )
        ]

        # 2. Relationship Memories
        prof_vance_rel = RelationshipMemory(
            entity_name="Prof. Xavier Vance",
            organization="MIT CSAIL",
            relationship_type="research_contact",
            associated_projects=["FieldChain", "Byzantine Consensus Limits"],
            preferred_communication_style="formal_academic",
            last_interaction_date="2026-09-16",
            notes=["Met at CCNCPS Distributed Systems session", "Discussed Byzantine quorum degradation"],
            confidence=0.96,
            sources=["contact_001", "cal_001", "gmail_001"]
        )

        dr_chen_rel = RelationshipMemory(
            entity_name="Dr. Sarah Chen",
            organization="UC Berkeley RISELab",
            relationship_type="research_contact",
            associated_projects=["Adaptive Sharding"],
            preferred_communication_style="formal",
            last_interaction_date="2026-08-20",
            notes=["Collaborated on initial sharding benchmark design"],
            confidence=0.94,
            sources=["contact_002", "gmail_012"]
        )

        # 3. Writing Style Memories
        default_styles = [
            MemoryItem(
                memory_id="mem_style_001",
                type=MemoryType.WRITING_STYLE,
                subject="Email Closing",
                fact="User consistently closes formal and academic emails with 'Best regards,' followed by affiliation.",
                confidence=0.95,
                sources=["gmail_001", "gmail_004"],
                lifecycle_status=LifecycleStatus.ACTIVE
            ),
            MemoryItem(
                memory_id="mem_style_002",
                type=MemoryType.WRITING_STYLE,
                subject="Paragraph Structure",
                fact="User prefers concise 1-3 sentence paragraphs with clean line-break spacing in LinkedIn posts.",
                confidence=0.92,
                sources=["linkedin_001", "linkedin_002"],
                lifecycle_status=LifecycleStatus.ACTIVE
            ),
            MemoryItem(
                memory_id="mem_style_003",
                type=MemoryType.WRITING_STYLE,
                subject="Hashtags & Emojis",
                fact="User typically uses 3-5 technical hashtags and low emoji frequency in public professional announcements.",
                confidence=0.91,
                sources=["linkedin_001", "linkedin_003"],
                lifecycle_status=LifecycleStatus.ACTIVE
            )
        ]

        for m in default_facts + default_styles:
            self._memories[m.memory_id] = m
        self._relationships[prof_vance_rel.entity_name.lower()] = prof_vance_rel
        self._relationships[dr_chen_rel.entity_name.lower()] = dr_chen_rel

    def get_all_memories(self) -> List[MemoryItem]:
        return list(self._memories.values())

    def get_relationship(self, entity_name: str) -> Optional[RelationshipMemory]:
        q = entity_name.lower()
        for key, rel in self._relationships.items():
            if q in key or key in q or any(q in alias.lower() for alias in [rel.entity_name]):
                return rel
        return None

    def add_memory(self, memory: MemoryItem) -> MemoryItem:
        self._memories[memory.memory_id] = memory
        self.save()
        return memory

    def add_relationship(self, rel: RelationshipMemory) -> RelationshipMemory:
        self._relationships[rel.entity_name.lower()] = rel
        self.save()
        return rel

    def save(self):
        if self.storage_path == ":memory:":
            return
        try:
            from datetime import timezone
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            payload = {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "memories": [m.model_dump() for m in self._memories.values()],
                "relationships": [r.model_dump() for r in self._relationships.values()]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"[MemoryStore] Save failed: {e}")
