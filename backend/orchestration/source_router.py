from typing import List, Dict, Any
from pydantic import BaseModel, Field
from backend.task.classifier import TaskRepresentation

class SourceDirective(BaseModel):
    source_category: str                    # "personal", "web", "memory"
    specific_source: str                    # "gmail", "calendar", "drive", "web", "memory"
    query: str                              # Targeted query string
    reason: str                             # Purpose of querying this source
    priority: int = 1                       # 1 = highest

class SourcePlan(BaseModel):
    directives: List[SourceDirective] = Field(default_factory=list)
    personal_sources: List[str] = Field(default_factory=list)
    external_sources: List[str] = Field(default_factory=list)
    memory_enabled: bool = True

class SourceRouter:
    """
    Source Router sitting at the top of the Orchestration Layer.
    Decomposes user writing tasks into three distinct knowledge streams:
      1. Personal Evidence ('What happened to me?') -> Gmail, Calendar, Drive
      2. External Evidence ('What is this thing?') -> Web Search, Conference Pages
      3. Memory & Style ('How do I express this?') -> Long-term memory & style profile
    """

    @classmethod
    def plan_sources(cls, task: TaskRepresentation) -> SourcePlan:
        directives: List[SourceDirective] = []
        personal_sources = []
        external_sources = []

        # 1. Memory is always queried first (zero-latency local prior)
        directives.append(SourceDirective(
            source_category="memory",
            specific_source="memory",
            query=f"{task.target_entity or ''} {task.topic or ''} {task.event_context or ''}".strip(),
            reason="Retrieve established facts, relationship profiles, and writing habits from persistent memory.",
            priority=1
        ))

        # 2. External Web Evidence (if conference, public event, or company mentioned)
        if task.event_context or "conference" in task.user_prompt.lower() or "ccncps" in task.user_prompt.lower():
            conf_query = task.event_context or "CCNCPS 2026 conference Dubai"
            directives.append(SourceDirective(
                source_category="web",
                specific_source="web",
                query=conf_query,
                reason="Establish official conference background, dates, venue, and track definitions.",
                priority=2
            ))
            external_sources.append("web")

        # 3. Personal Evidence via Connectors
        # Calendar: For dates and in-person attendance
        if task.event_context or "meeting" in task.user_prompt.lower() or "conference" in task.user_prompt.lower():
            directives.append(SourceDirective(
                source_category="personal",
                specific_source="calendar",
                query=f"{task.event_context or 'conference'} {task.target_entity or ''}".strip(),
                reason="Confirm attendance dates, sessions, and scheduled meetings.",
                priority=3
            ))
            personal_sources.append("calendar")

        # Gmail: For communication, interactions, and results
        directives.append(SourceDirective(
            source_category="personal",
            specific_source="gmail",
            query=f"{task.topic or 'research'} {task.target_entity or 'professor'} {task.event_context or ''}".strip(),
            reason="Retrieve personal email exchanges, feedback, and notifications.",
            priority=3
        ))
        personal_sources.append("gmail")

        # Drive: For technical papers, figures, and benchmark docs
        if task.topic or "paper" in task.user_prompt.lower() or "benchmark" in task.user_prompt.lower():
            directives.append(SourceDirective(
                source_category="personal",
                specific_source="drive",
                query=f"{task.topic or 'FieldChain'} benchmark report",
                reason="Retrieve documented benchmark numbers, TPS, and architecture specs.",
                priority=4
            ))
            personal_sources.append("drive")

        return SourcePlan(
            directives=directives,
            personal_sources=list(set(personal_sources)),
            external_sources=list(set(external_sources)),
            memory_enabled=True
        )
