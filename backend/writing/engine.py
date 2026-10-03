import os
from typing import Optional, Dict, Any
from pydantic import BaseModel

from backend.task.classifier import TaskRepresentation
from backend.evidence.state import EvidenceState
from backend.writing.profiles.style_profile import PersonalWritingProfile
from backend.writing.blueprints.blueprint_schema import WritingBlueprint
from backend.writing.blueprints.email_blueprint import EmailBlueprintBuilder
from backend.writing.blueprints.linkedin_blueprint import LinkedInBlueprintBuilder
from backend.writing.blueprints.generic_blueprint import GenericBlueprintBuilder
from backend.writing.verification.pipeline import MultiPassVerificationPipeline, MultiPassVerificationReport

try:
    from backend.generation.generation_runtime import DeterministicGroundedModel, OllamaGenerationModel
except ImportError:
    from generation.generation_runtime import DeterministicGroundedModel, OllamaGenerationModel

class WritingResult(BaseModel):
    final_draft: str
    blueprint: WritingBlueprint
    verification: MultiPassVerificationReport
    profile_used: PersonalWritingProfile

class WritingTaskEngine:
    """
    Writing Task Engine.
    Coordinates Writing Task Profiles, Blueprints, Style Fingerprints, Open-Weight Generation,
    and Multi-Pass Verification.
    """

    def __init__(self, profile: Optional[PersonalWritingProfile] = None):
        self.profile = profile or PersonalWritingProfile()
        self.local_generator = DeterministicGroundedModel()
        self.ollama = OllamaGenerationModel(model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))

    def execute_writing(
        self,
        task: TaskRepresentation,
        evidence: EvidenceState
    ) -> WritingResult:
        medium = "email"
        if task.site == "linkedin" or "linkedin" in task.user_prompt.lower():
            medium = "linkedin"
        elif task.site not in ["gmail", "email"]:
            medium = "generic"

        self.profile.active_medium = medium

        # Step 1: Build the specific blueprint
        if medium == "email":
            blueprint = EmailBlueprintBuilder.build(task, evidence, self.profile)
        elif medium == "linkedin":
            blueprint = LinkedInBlueprintBuilder.build(task, evidence, self.profile)
        else:
            blueprint = GenericBlueprintBuilder.build(task, evidence, self.profile)

        # Step 2: Render prompt combining blueprint instructions with evidence
        prompt_directive = blueprint.render_instruction_prompt()

        # Step 3: Open-Weight Generation (Ollama or deterministic grounded writer)
        raw_draft = None
        if os.getenv("USE_OLLAMA", "false").lower() == "true":
            try:
                raw_draft = self.ollama.generate(prompt=prompt_directive, context_evidence=evidence.items)
            except Exception:
                raw_draft = None

        if not raw_draft:
            raw_draft = self.local_generator.generate(prompt=prompt_directive, context_evidence=evidence.items)

        # Step 4: Multi-Pass Verification Pipeline
        verification_report = MultiPassVerificationPipeline.execute(
            raw_draft=raw_draft,
            blueprint=blueprint,
            evidence_items=evidence.items,
            profile=self.profile
        )

        return WritingResult(
            final_draft=verification_report.final_draft,
            blueprint=blueprint,
            verification=verification_report,
            profile_used=self.profile
        )
