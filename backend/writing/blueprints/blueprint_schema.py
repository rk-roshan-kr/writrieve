from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
try:
    from backend.writing.profiles.exemplars import WritingExemplar
except ImportError:
    from writing.profiles.exemplars import WritingExemplar

class WritingBlueprint(BaseModel):
    """
    The structured contract passed to the generation model.
    Encodes structure, evidence requirements, style fingerprint, and hard constraints.
    """
    blueprint_id: str
    medium: str                              # "email", "linkedin", "generic"
    task_category: str                       # "professional_followup", "conference_award", etc.
    target_audience: str                     # "academic_advisor", "professional_network", etc.
    
    # Structural Sequence (Grammar)
    structure_sequence: List[str]            # e.g. ["greeting", "hook", "shared_context", ...]
    
    # Grounding Contracts
    must_include_facts: List[str]            # Extracted strictly from verified EvidenceState
    must_not_invent: List[str] = Field(default_factory=lambda: [
        "Unverified commitments or promises",
        "Invented dates, locations, or paper titles",
        "Unconfirmed lab tour or funding offers"
    ])
    
    # Platform & Length Boundaries
    min_characters: int = 150
    max_characters: int = 3000
    target_characters: int = 450
    
    # Voice & Style Attributes
    formality_level: float = 0.70
    tone_description: str = "approachable_professional"
    formatting_rules: List[str] = Field(default_factory=list)
    
    # Style Compression Exemplars
    exemplars: List[WritingExemplar] = Field(default_factory=list)

    def render_instruction_prompt(self) -> str:
        """
        Renders the blueprint into an explicit execution directive for the LLM.
        """
        facts_str = "\n".join([f"- {f}" for f in self.must_include_facts])
        forbidden_str = "\n".join([f"- {f}" for f in self.must_not_invent])
        structure_str = " -> ".join(self.structure_sequence)
        rules_str = "\n".join([f"- {r}" for r in self.formatting_rules])
        
        exemplar_blocks = ""
        if self.exemplars:
            exemplar_blocks = "\n\nREPRESENTATIVE PERSONAL WRITING STYLE EXAMPLES (Adopt rhythm/voice, NOT facts):\n"
            for ex in self.exemplars[:2]:
                exemplar_blocks += f"---\n{ex.sample_text}\n"

        return f"""WRITING BLUEPRINT:
Medium: {self.medium.upper()}
Task: {self.task_category}
Target Audience: {self.target_audience}
Target Length: {self.target_characters} characters (Boundaries: {self.min_characters} - {self.max_characters} chars)

REQUIRED STRUCTURAL SEQUENCE:
{structure_str}

MANDATORY FACTS (Must be woven naturally into the text):
{facts_str}

FORBIDDEN EXTRAPOLATIONS (Strict Anti-Hallucination):
{forbidden_str}

STYLE & FORMATTING DIRECTIVES:
- Tone: {self.tone_description} (Formality: {self.formality_level})
{rules_str}
{exemplar_blocks}"""
