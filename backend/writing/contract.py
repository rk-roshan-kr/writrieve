import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AudienceSpec(BaseModel):
    recipient: Optional[str] = None
    relationship: str = "collaborator"  # e.g., professor, peer, executive, recruiter
    formality: float = 0.7              # 0.0 (casual) to 1.0 (academic/formal)

class StyleSpec(BaseModel):
    sentence_length: str = "medium (14-18 words)"
    paragraph_length: str = "short (1-2 sentences)"
    formality: float = 0.70
    enthusiasm: float = 0.55
    emoji: bool = False

class ConstraintSpec(BaseModel):
    max_words: int = 180
    min_words: int = 60
    platform: str = "email"             # "email", "linkedin", "generic"
    must_include_next_step: bool = True

class EvidenceClaim(BaseModel):
    claim: str
    source_id: str
    source_type: str                    # "gmail", "calendar", "drive", "memory", "web"

class WritingContract(BaseModel):
    """
    Formal Writing Contract delivered to the specialized writing model.
    Decouples WHAT must be said (Software/Task Engine) from HOW it is expressed (Model).
    """
    task_type: str                      # e.g., "email_followup", "linkedin_conference_post"
    purpose: str                        # e.g., "continue_research_discussion"
    audience: AudienceSpec = Field(default_factory=AudienceSpec)
    required_content: List[str] = Field(default_factory=list)
    forbidden_content: List[str] = Field(default_factory=lambda: [
        "invent achievements or unconfirmed testbed figures",
        "invent unconfirmed meeting commitments or agreements",
        "cite dates or locations not present in verified evidence"
    ])
    structure: List[str] = Field(default_factory=lambda: [
        "greeting",
        "context_acknowledgment",
        "specific_technical_followup",
        "next_step_proposal",
        "closing"
    ])
    style: StyleSpec = Field(default_factory=StyleSpec)
    constraints: ConstraintSpec = Field(default_factory=ConstraintSpec)
    evidence: List[EvidenceClaim] = Field(default_factory=list)

    def render_prompt_contract(self) -> str:
        """Renders the Writing Contract into an explicit, unambiguous instruction spec for the model."""
        req_block = "\n".join([f"  - {r}" for r in self.required_content])
        forbid_block = "\n".join([f"  - {f}" for f in self.forbidden_content])
        struct_block = " -> ".join(self.structure)
        evidence_block = "\n".join([f"  - [{e.source_type.upper()}] {e.claim} (Source: {e.source_id})" for e in self.evidence])

        return f"""=== WRITE4U FORMAL WRITING CONTRACT ===
TASK: {self.task_type} (Purpose: {self.purpose})
AUDIENCE: {self.audience.relationship} (Formality: {self.audience.formality})
CONSTRAINTS: {self.constraints.min_words}-{self.constraints.max_words} words | Platform: {self.constraints.platform}

REQUIRED SECTIONS:
{struct_block}

VERIFIED EVIDENCE (Use strictly):
{evidence_block}

REQUIRED TOPICS TO COVER:
{req_block}

STRICT FORBIDDEN CONTENT (Zero Hallucination Guard):
{forbid_block}

STYLE GUIDELINES:
- Sentence length: {self.style.sentence_length}
- Paragraph style: {self.style.paragraph_length}
- Formality: {self.style.formality} | Enthusiasm: {self.style.enthusiasm} | Emojis: {self.style.emoji}

INSTRUCTION: Produce natural, publication-ready prose strictly conforming to this contract. Do not include markdown code block quotes around the prose.
"""
