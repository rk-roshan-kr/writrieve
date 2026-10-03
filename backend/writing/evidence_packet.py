from typing import List, Dict, Any
from pydantic import BaseModel, Field
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class FactEntry(BaseModel):
    text: str
    source_id: str
    source_type: str                         # "personal", "web", "memory"
    confidence: float

class WritingEvidencePacket(BaseModel):
    """
    Distilled Evidence Packet delivered to the specialized writing model.
    Contains verified facts, personal experience signals, external background,
    and explicit anti-hallucination boundaries.
    """
    task_name: str
    facts: List[FactEntry] = Field(default_factory=list)
    personal_experience: List[str] = Field(default_factory=list)
    external_context: List[str] = Field(default_factory=list)
    uncertain_facets: List[str] = Field(default_factory=list)
    forbidden_claims: List[str] = Field(default_factory=lambda: [
        "Do not invent unverified attendee interactions or unconfirmed meetings",
        "Do not invent funding amounts or unverified lab tour invitations",
        "Do not invent co-authors or awards not present in verified facts"
    ])

    @classmethod
    def compile(cls, task_name: str, evidence_items: List[ContextItem]) -> "WritingEvidencePacket":
        facts: List[FactEntry] = []
        personal_exp: List[str] = []
        ext_ctx: List[str] = []

        for item in evidence_items:
            clean_fact = item.content.split("\n")[0].strip()
            source_cat = "web" if item.source == "web" else ("memory" if item.source == "personal_memory" else "personal")

            facts.append(FactEntry(
                text=clean_fact,
                source_id=item.id,
                source_type=source_cat,
                confidence=item.reliability
            ))

            if source_cat == "personal":
                personal_exp.append(f"[{item.source.upper()}] {clean_fact}")
            elif source_cat == "web":
                ext_ctx.append(f"[WEB] {clean_fact}")
            elif source_cat == "memory":
                personal_exp.append(f"[MEMORY] {clean_fact}")

        return WritingEvidencePacket(
            task_name=task_name,
            facts=facts,
            personal_experience=personal_exp,
            external_context=ext_ctx
        )

    def render_prompt_section(self) -> str:
        facts_block = "\n".join([f"- [{f.source_type.upper()}] {f.text} (Source: {f.source_id})" for f in self.facts])
        forbidden_block = "\n".join([f"- {c}" for c in self.forbidden_claims])

        return f"""EVIDENCE PACKET:
{facts_block}

FORBIDDEN EXTRAPOLATIONS (Strict Anti-Hallucination):
{forbidden_block}"""
