from typing import List, Dict, Any
from pydantic import BaseModel, Field

from backend.writing.blueprints.blueprint_schema import WritingBlueprint
from backend.writing.profiles.style_profile import PersonalWritingProfile
from .style_verifier import StyleVerifier, StyleVerificationResult
from .factual_verifier import FactualVerifier, FactualVerificationResult
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class MultiPassVerificationReport(BaseModel):
    final_draft: str
    overall_status: str                       # "PASSED", "WARNING", "REJECTED"
    pass_1_platform: bool
    pass_2_structure: bool
    pass_3_length: bool
    pass_4_factual: bool
    pass_5_style: bool
    style_report: StyleVerificationResult
    factual_report: FactualVerificationResult
    feedback_notes: List[str] = Field(default_factory=list)

class MultiPassVerificationPipeline:
    """
    Orchestrates the multi-pass verification pipeline:
      Pass 1: Platform Limits Check (hard cap)
      Pass 2: Structural Sequence Check (greeting, context, next step, closing)
      Pass 3: Length Target Check
      Pass 4: Factual Grounding & Hallucination Pruning
      Pass 5: User Style Fingerprint Alignment
    """

    @classmethod
    def execute(
        cls,
        raw_draft: str,
        blueprint: WritingBlueprint,
        evidence_items: List[ContextItem],
        profile: PersonalWritingProfile
    ) -> MultiPassVerificationReport:
        notes = []

        # Step 1: Factual verification & claim cleanup
        factual_res = FactualVerifier.verify(draft=raw_draft, evidence_items=evidence_items)
        if factual_res.has_unsupported_claims:
            notes.append(f"Pruned {factual_res.unsupported_count} unverified claim(s) from draft.")

        active_draft = factual_res.verified_draft

        # Step 2: Style, structural, and platform verification
        style_res = StyleVerifier.verify(
            draft=active_draft,
            blueprint=blueprint,
            profile=profile
        )

        if not style_res.platform_valid:
            notes.append("Warning: Draft exceeded platform character cap.")
        if not style_res.structure_valid:
            notes.append(f"Notice: Missing structural sections: {', '.join(style_res.missing_sections)}.")

        overall_status = "PASSED"
        if not style_res.platform_valid or factual_res.grounding_ratio < 0.5:
            overall_status = "REJECTED"
        elif not style_res.structure_valid or factual_res.has_unsupported_claims:
            overall_status = "WARNING"

        return MultiPassVerificationReport(
            final_draft=active_draft,
            overall_status=overall_status,
            pass_1_platform=style_res.platform_valid,
            pass_2_structure=style_res.structure_valid,
            pass_3_length=style_res.length_valid,
            pass_4_factual=not factual_res.has_unsupported_claims,
            pass_5_style=style_res.style_aligned,
            style_report=style_res,
            factual_report=factual_res,
            feedback_notes=notes
        )
