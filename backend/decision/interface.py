from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class DecisionActionType(str, Enum):
    QUERY_SOURCE = "QUERY_SOURCE"
    REFINE_QUERY = "REFINE_QUERY"
    FETCH_ITEM = "FETCH_ITEM"
    EXPAND_ENTITY = "EXPAND_ENTITY"
    CHECK_ANOTHER_SOURCE = "CHECK_ANOTHER_SOURCE"
    VERIFY_CONFLICT = "VERIFY_CONFLICT"
    STOP = "STOP"
    ABSTAIN = "ABSTAIN"
    ASK_USER = "ASK_USER"

class DecisionAction(BaseModel):
    action: DecisionActionType
    source: Optional[str] = None
    query: Optional[str] = None
    reason: str
    confidence: float = 0.90
    metadata: Dict[str, Any] = Field(default_factory=dict)
