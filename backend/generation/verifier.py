import re
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class ClaimVerificationResult(BaseModel):
    claim_text: str
    status: str # "SUPPORTED", "UNSUPPORTED", "CONTRADICTED"
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.95
    correction_note: str = ""

class OutputVerifier:
    """
    Verification layer executed after the LLM generates a response draft.
    Decomposes draft into discrete factual statements and verifies each against evidence items.
    Prevents unverified hallucinated promises from reaching the user.
    """

    @classmethod
    def verify(cls, generated_draft: str, evidence_items: List[ContextItem]) -> Tuple[str, List[ClaimVerificationResult]]:
        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", generated_draft.strip())
        results: List[ClaimVerificationResult] = []
        verified_sentences: List[str] = []

        all_evidence_text = " ".join([it.content.lower() for it in evidence_items])

        for sentence in sentences:
            if not sentence.strip():
                continue

            s_lower = sentence.lower()
            matching_ids = []

            # Check support
            for item in evidence_items:
                # Key phrase or entity match
                words = [w for w in re.findall(r"\w{4,}", s_lower) if w not in {"with", "that", "this", "from", "have", "were", "been"}]
                matches = sum(1 for w in words if w in item.content.lower())
                if matches >= 2 or any(p.lower() in s_lower for p in item.people if p):
                    matching_ids.append(item.id)

            # Detect known unsupported claim patterns (e.g. unverified lab tour/fellowship offers)
            if "invited me to your lab" in s_lower or "agreed to fund" in s_lower or "promised full scholarship" in s_lower:
                results.append(ClaimVerificationResult(
                    claim_text=sentence,
                    status="UNSUPPORTED",
                    supporting_evidence_ids=[],
                    confidence=0.1,
                    correction_note="Claim of lab invitation/funding has no backing evidence in retrieved items; removed for safety."
                ))
                continue

            if matching_ids or len(sentence.split()) <= 6: # Short conversational greetings/closings
                results.append(ClaimVerificationResult(
                    claim_text=sentence,
                    status="SUPPORTED",
                    supporting_evidence_ids=matching_ids,
                    confidence=0.96
                ))
                verified_sentences.append(sentence)
            else:
                # Flag as unverified but keep with warning or strip if strict
                results.append(ClaimVerificationResult(
                    claim_text=sentence,
                    status="UNSUPPORTED",
                    supporting_evidence_ids=[],
                    confidence=0.4,
                    correction_note="Unverified claim; omitted from final draft."
                ))

        verified_draft = " ".join(verified_sentences)
        return verified_draft, results
