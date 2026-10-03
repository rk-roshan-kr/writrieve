from typing import Dict, Any
from pydantic import BaseModel, Field
from backend.writing.blueprints.blueprint_schema import WritingBlueprint
from backend.writing.profiles.style_profile import PersonalWritingProfile
from backend.writing.constraints.platform import PlatformConstraints
from backend.writing.constraints.length import LengthConstraints
from backend.writing.constraints.structure import StructureConstraints
from backend.writing.constraints.style_rules import StyleConstraints

class StyleVerificationResult(BaseModel):
    passed: bool
    platform_valid: bool
    structure_valid: bool
    length_valid: bool
    style_aligned: bool
    length_score: float = 1.0
    satisfied_sections: list[str] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    diagnostics: Dict[str, Any] = Field(default_factory=dict)
    summary: str = ""

class StyleVerifier:
    """
    Evaluates generated drafts against platform constraints, structural grammar,
    length targets, and user profile habits.
    """

    @classmethod
    def verify(
        cls,
        draft: str,
        blueprint: WritingBlueprint,
        profile: PersonalWritingProfile
    ) -> StyleVerificationResult:
        # 1. Platform limit
        plat_ok, plat_msg = PlatformConstraints.validate(draft, blueprint.medium)

        # 2. Length boundary
        len_ok, len_score, len_msg = LengthConstraints.evaluate(
            draft,
            blueprint.min_characters,
            blueprint.max_characters,
            blueprint.target_characters
        )

        # 3. Structure
        struct_ok, satisfied, missing = StructureConstraints.evaluate(
            draft,
            blueprint.medium,
            blueprint.structure_sequence
        )

        # 4. Style drift
        style_ok, diag, style_msg = StyleConstraints.evaluate(draft, profile)

        all_passed = plat_ok and struct_ok and len_ok and style_ok

        summary = f"{plat_msg} {len_msg} {style_msg}"
        if missing:
            summary += f" Missing structural elements: {', '.join(missing)}."

        return StyleVerificationResult(
            passed=all_passed,
            platform_valid=plat_ok,
            structure_valid=struct_ok,
            length_valid=len_ok,
            style_aligned=style_ok,
            length_score=len_score,
            satisfied_sections=satisfied,
            missing_sections=missing,
            diagnostics=diag,
            summary=summary.strip()
        )
