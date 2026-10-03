from typing import List
from backend.task.classifier import TaskRepresentation
from backend.evidence.state import EvidenceState
from backend.writing.profiles.style_profile import PersonalWritingProfile
from backend.writing.profiles.exemplars import ExemplarStore
from .blueprint_schema import WritingBlueprint

class LinkedInBlueprintBuilder:
    """
    Constructs task-specific WritingBlueprints for LinkedIn posts.
    Grammar: Hook -> Announcement / Story -> Key Metrics -> Acknowledgements -> Open-Source/CTA -> Hashtags.
    """

    @classmethod
    def build(
        cls,
        task: TaskRepresentation,
        evidence: EvidenceState,
        profile: PersonalWritingProfile
    ) -> WritingBlueprint:
        category = "conference_award"
        if "announc" in task.user_prompt.lower():
            category = "project_announcement"
        elif "research" in task.user_prompt.lower() or "update" in task.user_prompt.lower():
            category = "research_update"

        sequence = [
            "declarative_hook",
            "achievement_or_context",
            "technical_metrics_and_takeaway",
            "collaborator_gratitude",
            "open_source_or_cta",
            "hashtags"
        ]

        facts = []
        for item in evidence.items[:4]:
            first_line = item.content.split("\n")[0]
            if len(first_line) > 10:
                facts.append(first_line[:120])
        if not facts:
            facts = ["CCNCPS 2026 conference presentation", "FieldChain 19.4k TPS benchmark"]

        formatting = [
            "Start with high-impact declarative first line (the hook)",
            "Use line breaks between short 1-2 sentence paragraphs",
            "Include concrete benchmarks or numerical data points",
            "Tag or mention collaborators with gratitude",
            f"End with exactly {profile.linkedin.typical_hashtag_count} relevant technical hashtags (e.g. #DistributedSystems #Research)"
        ]

        exemplars = ExemplarStore.get_exemplars(medium="linkedin", category=category)

        return WritingBlueprint(
            blueprint_id=f"blueprint_linkedin_{category}",
            medium="linkedin",
            task_category=category,
            target_audience="professional_and_research_network",
            structure_sequence=sequence,
            must_include_facts=facts,
            min_characters=400,
            max_characters=profile.linkedin.hard_char_limit,  # 3000 cap
            target_characters=profile.linkedin.avg_length_chars or 1140,
            formality_level=0.55,
            tone_description=task.desired_tone or "enthusiastic_professional",
            formatting_rules=formatting,
            exemplars=exemplars
        )
