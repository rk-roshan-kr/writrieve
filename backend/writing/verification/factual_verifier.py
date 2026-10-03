from typing import List, Tuple
from pydantic import BaseModel, Field
from backend.generation.verifier import OutputVerifier, ClaimVerificationResult
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class FactualVerificationResult(BaseModel):
    verified_draft: str
    claims: List[ClaimVerificationResult] = Field(default_factory=list)
    has_unsupported_claims: bool = False
    unsupported_count: int = 0
    supported_count: int = 0
    grounding_ratio: float = 1.0

class FactualVerifier:
    """
    Decomposes draft into claims and verifies them against the provided Evidence items.
    Prunes hallucinated promises and calculates grounding ratio.
    """

    @classmethod
    def verify(cls, draft: str, evidence_items: List[ContextItem]) -> FactualVerificationResult:
        cleaned_draft, claims = OutputVerifier.verify(
            generated_draft=draft,
            evidence_items=evidence_items
        )

        unsupported = [c for c in claims if c.status == "UNSUPPORTED"]
        supported = [c for c in claims if c.status == "SUPPORTED"]

        total = len(claims) or 1
        grounding_ratio = round(len(supported) / total, 2)

        return FactualVerificationResult(
            verified_draft=cleaned_draft,
            claims=claims,
            has_unsupported_claims=len(unsupported) > 0,
            unsupported_count=len(unsupported),
            supported_count=len(supported),
            grounding_ratio=grounding_ratio
        )
