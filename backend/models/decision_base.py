from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class DecisionRequest(BaseModel):
    question: str
    state: Dict[str, Any] = Field(default_factory=dict)
    options: Optional[List[str]] = Field(default_factory=lambda: ["yes", "no"])

class DecisionResponse(BaseModel):
    decision: str
    probability: float
    probabilities: Dict[str, float]
    latency_ms: float
    model_name: str
    rationale: Optional[str] = None

class DecisionModel(ABC):
    """
    Abstract System-1 Decision Model Interface.
    Executes typed, high-frequency, bounded decisions (yes/no, categorical choice, probability ratings)
    without generating conversational prose.
    """

    @abstractmethod
    def decide(self, state: Dict[str, Any], question: str, options: Optional[List[str]] = None) -> DecisionResponse:
        pass

class GenerationModel(ABC):
    """
    Abstract Generation Model Interface (Ollama / vLLM / Remote).
    Generates grounded text conditioned strictly on verified evidence.
    """

    @abstractmethod
    def generate(self, prompt: str, context_evidence: List[Any], page_context: Optional[Dict[str, Any]] = None) -> str:
        pass
