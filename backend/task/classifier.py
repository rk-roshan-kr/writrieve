from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TaskClass(str, Enum):
    CLASS_A_LOOKUP = "class_a_lookup"            # Exact factual retrieval (e.g. "What time is my meeting?")
    CLASS_B_SYNTHESIS = "class_b_synthesis"      # Multi-source aggregation (e.g. "Summarize my work with Prof X")
    CLASS_C_GENERATION = "class_c_generation"    # Context-grounded writing (e.g. "Write a follow-up email")
    CLASS_D_AMBIGUOUS = "class_d_ambiguous"      # Under-specified entities (e.g. "Email Rahul")
    CLASS_E_SENSITIVE = "class_e_sensitive"      # High privacy/financial inquiry

class TaskRepresentation(BaseModel):
    user_prompt: str
    site: str = "gmail"
    task_class: TaskClass = TaskClass.CLASS_C_GENERATION
    target_entity: Optional[str] = None
    target_aliases: List[str] = Field(default_factory=list)
    event_context: Optional[str] = None
    topic: Optional[str] = None
    desired_tone: str = "professional"
    constraints: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    risk_level: str = "low"
    freshness_preference: str = "balanced"  # "strict_recent", "balanced", "historical_ok"
