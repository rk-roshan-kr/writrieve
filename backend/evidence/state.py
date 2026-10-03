from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class TerminalStatus(str, Enum):
    INITIALIZING = "INITIALIZING"
    ACQUIRING = "ACQUIRING"
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    ASK_USER = "ASK_USER"
    ABSTAIN = "ABSTAIN"
    FAILED = "FAILED"

class ClaimEvidence(BaseModel):
    claim: str
    sources: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.9
    status: str = "KNOWN" # "KNOWN", "INFERRED", "CONFLICTING", "UNKNOWN"

class EvidenceConflict(BaseModel):
    field: str
    values: List[str]
    source_mappings: Dict[str, str]
    resolution_status: str = "UNRESOLVED" # "RESOLVED", "UNRESOLVED"
    resolved_value: Optional[str] = None

class EvidenceState(BaseModel):
    task_id: str = "task_001"
    claims: List[ClaimEvidence] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    conflicts: List[EvidenceConflict] = Field(default_factory=list)
    sources_used: List[str] = Field(default_factory=list)
    items: List[ContextItem] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    terminal_status: TerminalStatus = TerminalStatus.INITIALIZING
    clarification_prompt: Optional[str] = None
    iteration: int = 0

    def add_claim(self, claim: str, sources: List[str], evidence_ids: List[str], confidence: float = 0.9):
        self.claims.append(ClaimEvidence(
            claim=claim,
            sources=sources,
            evidence_ids=evidence_ids,
            confidence=confidence,
            status="KNOWN"
        ))

    def mark_unknown(self, unknown: str):
        if unknown not in self.unknowns:
            self.unknowns.append(unknown)

    def resolve_unknown(self, unknown: str):
        if unknown in self.unknowns:
            self.unknowns.remove(unknown)

    def add_conflict(self, field: str, values: List[str], mappings: Dict[str, str]):
        self.conflicts.append(EvidenceConflict(
            field=field,
            values=values,
            source_mappings=mappings
        ))

    def overall_sufficiency(self) -> float:
        if not self.confidence_scores:
            return 0.0
        scores = list(self.confidence_scores.values())
        return round(sum(scores) / len(scores), 2)
