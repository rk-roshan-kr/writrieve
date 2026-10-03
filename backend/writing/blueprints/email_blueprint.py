from typing import List, Dict, Any, Optional
from backend.task.classifier import TaskRepresentation
from backend.evidence.state import EvidenceState
from backend.writing.profiles.style_profile import PersonalWritingProfile
from backend.writing.profiles.exemplars import ExemplarStore
from .blueprint_schema import WritingBlueprint

class EmailBlueprintBuilder:
    """
    Constructs task-specific WritingBlueprints for Email communication.
    Grammar: Greeting -> Thank You / Context -> Research / Subject -> Next Step -> Sign-off.
    """

    @classmethod
    def build(
        cls,
        task: TaskRepresentation,
        evidence: EvidenceState,
        profile: PersonalWritingProfile
    ) -> WritingBlueprint:
        # Determine category
        category = "professional_followup"
        if "meeting" in task.user_prompt.lower() or "schedule" in task.user_prompt.lower():
            category = "meeting_request"
        elif "intro" in task.user_prompt.lower():
            category = "introduction"

        # Structural sequence
        sequence = [
            "greeting",
            "thank_you_or_context",
            "technical_discussion",
            "proposed_next_step",
            "closing_signoff"
        ]

        # Extract mandatory facts from evidence items
        facts = []
        for item in evidence.items[:4]:
            # Extract first sentence or headline
            first_line = item.content.split("\n")[0]
            if len(first_line) > 10:
                facts.append(first_line[:120])
        if not facts:
            facts = ["Recent collaboration at conference", "FieldChain project"]

        # Formatting rules from profile
        formatting = [
            f"Use formal greeting: {profile.email.greeting_patterns[0].format(name=task.target_entity or 'Professor')}",
            f"Use closing: {profile.email.closing_patterns[0]}",
            "Keep paragraphs concise (2-3 sentences max)",
            f"Include signature: {profile.email.signature_format.format(user_name=profile.user_name)}"
        ]

        exemplars = ExemplarStore.get_exemplars(medium="email", category=category)

        return WritingBlueprint(
            blueprint_id=f"blueprint_email_{category}",
            medium="email",
            task_category=category,
            target_audience="academic_or_industry_mentor",
            structure_sequence=sequence,
            must_include_facts=facts,
            min_characters=200,
            max_characters=900,
            target_characters=profile.email.avg_length_chars or 450,
            formality_level=profile.email.formality,
            tone_description=task.desired_tone,
            formatting_rules=formatting,
            exemplars=exemplars
        )
