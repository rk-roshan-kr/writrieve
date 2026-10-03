from typing import List
from backend.task.classifier import TaskRepresentation
from backend.evidence.state import EvidenceState
from backend.writing.profiles.style_profile import PersonalWritingProfile
from .blueprint_schema import WritingBlueprint

class GenericBlueprintBuilder:
    """
    Fallback blueprint builder for arbitrary professional writing (bios, summaries, abstracts).
    """

    @classmethod
    def build(
        cls,
        task: TaskRepresentation,
        evidence: EvidenceState,
        profile: PersonalWritingProfile
    ) -> WritingBlueprint:
        sequence = ["summary_statement", "supporting_evidence", "takeaway_or_closing"]
        facts = [it.content.split("\n")[0][:100] for it in evidence.items[:3]]

        return WritingBlueprint(
            blueprint_id="blueprint_generic_professional",
            medium="generic",
            task_category="professional_summary",
            target_audience="general_professional",
            structure_sequence=sequence,
            must_include_facts=facts,
            min_characters=150,
            max_characters=1500,
            target_characters=500,
            formality_level=0.70,
            tone_description=task.desired_tone,
            formatting_rules=["Clear paragraph structure", "Active voice"],
            exemplars=[]
        )
