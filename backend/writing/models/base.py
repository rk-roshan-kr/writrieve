from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel

try:
    from backend.writing.contract import WritingContract
except ImportError:
    from writing.contract import WritingContract

class WritingOutput(BaseModel):
    draft: str
    model_name: str
    tokens_used: int
    latency_ms: float
    sections: Optional[Dict[str, str]] = None

class WritingModel(ABC):
    """
    Abstract Writing Model Interface.
    Enforces a swappable layer across local open-weight writers (Qwen2.5, Gemma, Mistral)
    and remote inference engines.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def generate(self, contract: WritingContract, revision_directive: Optional[str] = None) -> WritingOutput:
        """
        Generate grounded prose strictly satisfying the given WritingContract.
        If revision_directive is supplied, incorporates targeted revision feedback.
        """
        pass
