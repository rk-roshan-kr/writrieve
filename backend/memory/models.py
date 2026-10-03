from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class MemoryType(str, Enum):
    FACTUAL = "factual"                     # Stable user facts (e.g. "User works on FieldChain consensus")
    RELATIONSHIP = "relationship"           # Person-specific interaction models (e.g. "Prof. Xavier Vance -> MIT CSAIL")
    WRITING_STYLE = "writing_style"         # Learned stylistic preferences (e.g. "Prefers short paragraphs, no emojis")
    TASK = "task"                           # Recent task context / pending follow-ups

class LifecycleStatus(str, Enum):
    NEW = "NEW"
    CANDIDATE = "CANDIDATE"
    CONFIRMED = "CONFIRMED"
    ACTIVE = "ACTIVE"
    STALE = "STALE"
    ARCHIVED = "ARCHIVED"

class MemoryItem(BaseModel):
    memory_id: str
    type: MemoryType
    subject: str                            # Entity or topic key (e.g. "Prof. Xavier Vance", "FieldChain", "LinkedIn")
    fact: str                               # The distilled stable knowledge claim
    confidence: float = 0.90                # Confidence score in [0.0, 1.0]
    sources: List[str] = Field(default_factory=list) # Provenance IDs (e.g. ["gmail_001", "cal_001"])
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_confirmed: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None
    lifecycle_status: LifecycleStatus = LifecycleStatus.ACTIVE
    access_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def touch(self):
        self.access_count += 1
        self.last_confirmed = datetime.now(timezone.utc).isoformat()

class RelationshipMemory(BaseModel):
    entity_name: str
    organization: Optional[str] = None
    relationship_type: str = "research_contact" # "research_contact", "advisor", "colleague", "recruiter"
    associated_projects: List[str] = Field(default_factory=list)
    preferred_communication_style: str = "formal"
    last_interaction_date: Optional[str] = None
    notes: List[str] = Field(default_factory=list)
    confidence: float = 0.95
    sources: List[str] = Field(default_factory=list)
