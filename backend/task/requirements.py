from typing import List, Dict, Any
from pydantic import BaseModel, Field
from .classifier import TaskRepresentation

class InformationRequirement(BaseModel):
    name: str                     # e.g. "recipient_identity", "prior_interaction", "project_topic", "date_confirmation"
    description: str
    target_sources: List[str]     # e.g. ["calendar", "gmail", "contacts"]
    mandatory: bool = True
    satisfied: bool = False
    evidence_item_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.0

class RequirementsPlanner:
    """
    Deconstructs a TaskRepresentation into explicit information requirements that the
    iterative retrieval loop must satisfy.
    """

    @classmethod
    def derive_requirements(cls, task: TaskRepresentation) -> List[InformationRequirement]:
        reqs: List[InformationRequirement] = []

        # 1. Identity confirmation
        reqs.append(InformationRequirement(
            name="recipient_identity",
            description=f"Resolve exact identity, name, and email for {task.target_entity or 'recipient'}",
            target_sources=["contacts", "calendar", "gmail"],
            mandatory=True
        ))

        # 2. Prior interaction / context
        reqs.append(InformationRequirement(
            name="prior_interaction",
            description=f"Find verified recent meetings, conversations, or exchanges regarding {task.event_context or 'recent interaction'}",
            target_sources=["calendar", "gmail"],
            mandatory=True
        ))

        # 3. Project / topic evidence
        if task.topic or "project" in task.user_prompt.lower():
            reqs.append(InformationRequirement(
                name="topic_context",
                description=f"Find documented artifacts, papers, or shared tasks on {task.topic or 'the active project'}",
                target_sources=["drive", "gmail", "github"],
                mandatory=True
            ))

        # 4. Social / background connection (optional)
        if task.site == "linkedin" or "linkedin" in task.user_prompt.lower():
            reqs.append(InformationRequirement(
                name="social_connection",
                description="Profile headlines, affiliations, or shared community posts",
                target_sources=["linkedin"],
                mandatory=False
            ))

        return reqs
