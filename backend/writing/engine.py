import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from backend.task.classifier import TaskRepresentation
from backend.evidence.state import EvidenceState
from backend.writing.profiles.style_profile import PersonalWritingProfile
from backend.writing.blueprints.blueprint_schema import WritingBlueprint
from backend.writing.blueprints.email_blueprint import EmailBlueprintBuilder
from backend.writing.blueprints.linkedin_blueprint import LinkedInBlueprintBuilder
from backend.writing.blueprints.generic_blueprint import GenericBlueprintBuilder
from backend.writing.contract import WritingContract, AudienceSpec, StyleSpec, ConstraintSpec, EvidenceClaim
from backend.writing.models.local_writer import LocalGroundedWriter
from backend.writing.models.remote_writer import RemoteOllamaWriter
from backend.writing.verification.pipeline import MultiPassVerificationPipeline, MultiPassVerificationReport

class WritingResult(BaseModel):
    final_draft: str
    blueprint: WritingBlueprint
    contract: WritingContract
    verification: MultiPassVerificationReport
    profile_used: PersonalWritingProfile
    targeted_revision_applied: bool = False

class WritingTaskEngine:
    """
    Writing Task Engine.
    Coordinates Writing Task Profiles, Blueprints, Style Fingerprints, Writing Contracts,
    Swappable Writing Models, and Closed-Loop Multi-Pass Verification.
    """

    def __init__(self, profile: Optional[PersonalWritingProfile] = None):
        self.profile = profile or PersonalWritingProfile()
        self.local_writer = LocalGroundedWriter()
        self.remote_writer = RemoteOllamaWriter(model_name=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))

    def compile_contract(
        self,
        task: TaskRepresentation,
        evidence: EvidenceState,
        medium: str
    ) -> WritingContract:
        """Assembles the formal Writing Contract specifying WHAT to write and WHAT is forbidden."""
        claims: List[EvidenceClaim] = []
        for item in evidence.items:
            claims.append(EvidenceClaim(
                claim=item.content.split("\n")[0].strip(),
                source_id=item.id,
                source_type=item.source
            ))

        task_name = task.task_class.value if hasattr(task.task_class, "value") else str(task.task_class)
        required_topics = [
            f"Address task: {task_name}",
        ]
        if task.target_entity:
            required_topics.append(f"Direct communication to or about {task.target_entity}")
        for c in claims[:3]:
            required_topics.append(f"Incorporate verified evidence: {c.claim[:60]}")

        formality = self.profile.email.formality if medium == "email" else 0.65
        max_w = self.profile.linkedin.hard_char_limit // 5 if medium == "linkedin" else 180

        return WritingContract(
            task_type=f"{medium}_{task_name}",
            purpose=task_name,
            audience=AudienceSpec(
                recipient=task.target_entity,
                relationship="professor" if "prof" in (task.target_entity or "").lower() else "peer",
                formality=formality
            ),
            required_content=required_topics,
            forbidden_content=[
                "invent unconfirmed achievements or unpublished figures",
                "invent unverified meeting commitments or agreements",
                "cite dates or locations not present in verified evidence"
            ],
            structure=[
                "greeting",
                "context_acknowledgment",
                "technical_discussion",
                "next_step_proposal",
                "closing"
            ] if medium == "email" else [
                "announcement_hook",
                "technical_achievement_body",
                "collaborator_gratitude",
                "open_source_cta",
                "hashtags"
            ],
            style=StyleSpec(
                sentence_length="14-18 words",
                paragraph_length="short (1-2 sentences)",
                formality=formality,
                enthusiasm=0.60,
                emoji=medium == "linkedin"
            ),
            constraints=ConstraintSpec(
                max_words=max_w,
                min_words=50,
                platform=medium
            ),
            evidence=claims
        )

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

        # Step 1: Build Blueprint
        if medium == "email":
            blueprint = EmailBlueprintBuilder.build(task, evidence, self.profile)
        elif medium == "linkedin":
            blueprint = LinkedInBlueprintBuilder.build(task, evidence, self.profile)
        else:
            blueprint = GenericBlueprintBuilder.build(task, evidence, self.profile)

        # Step 2: Compile Formal Writing Contract
        contract = self.compile_contract(task, evidence, medium)

        # Step 3: Writer Model Generation
        use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        writer = self.remote_writer if use_ollama else self.local_writer

        writer_output = writer.generate(contract)
        raw_draft = writer_output.draft

        # Step 4: Multi-Pass Verification Pipeline
        verification_report = MultiPassVerificationPipeline.execute(
            raw_draft=raw_draft,
            blueprint=blueprint,
            evidence_items=evidence.items,
            profile=self.profile
        )

        # Step 5: Closed-Loop Targeted Revision if any pass flagged an issue
        targeted_revision = False
        if not verification_report.all_passed:
            directive_parts = [f"- Resolve: {f}" for f in verification_report.failures]
            directive_parts.extend([f"- Feedback: {note}" for note in verification_report.feedback_notes])
            revision_directive = "\n".join(directive_parts)

            # Targeted re-generation with specific correction directives
            revised_output = writer.generate(contract, revision_directive=revision_directive)
            revised_report = MultiPassVerificationPipeline.execute(
                raw_draft=revised_output.draft,
                blueprint=blueprint,
                evidence_items=evidence.items,
                profile=self.profile
            )
            raw_draft = revised_report.final_draft
            verification_report = revised_report
            targeted_revision = True
        else:
            raw_draft = verification_report.final_draft

        return WritingResult(
            final_draft=raw_draft,
            blueprint=blueprint,
            contract=contract,
            verification=verification_report,
            profile_used=self.profile,
            targeted_revision_applied=targeted_revision
        )
