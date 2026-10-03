import os
from typing import List, Dict, Any, Tuple
from .prompts import PromptBuilder, SYSTEM_PROMPT_FIREWALL
from .verifier import OutputVerifier, ClaimVerificationResult
try:
    from backend.models.schemas import ContextItem
    from backend.generation.generation_runtime import DeterministicGroundedModel, OllamaGenerationModel
except ImportError:
    from models.schemas import ContextItem
    from generation.generation_runtime import DeterministicGroundedModel, OllamaGenerationModel

class ContextGroundedWriter:
    """
    Writer coordinating prompt creation with injection boundaries, open-weight model generation,
    and post-generation claim verification.
    """

    def __init__(self):
        self.local_generator = DeterministicGroundedModel()
        self.ollama = OllamaGenerationModel(model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))

    def write_and_verify(
        self,
        user_prompt: str,
        evidence_items: List[ContextItem],
        tone: str = "professional"
    ) -> Tuple[str, List[ClaimVerificationResult]]:
        # 1. Build injection-safe user prompt
        prompt = PromptBuilder.format_prompt(
            user_prompt=user_prompt,
            evidence_items=evidence_items,
            tone=tone
        )

        # 2. Generate raw draft via open-weight model or local deterministic grounded fallback
        raw_draft = None
        if os.getenv("USE_OLLAMA", "false").lower() == "true":
            try:
                raw_draft = self.ollama.generate(prompt=prompt, context_evidence=evidence_items)
            except Exception:
                raw_draft = None

        if not raw_draft:
            raw_draft = self.local_generator.generate(prompt=prompt, context_evidence=evidence_items)

        # 3. Output verification layer: decompose claims and verify
        verified_draft, claims_verifications = OutputVerifier.verify(
            generated_draft=raw_draft,
            evidence_items=evidence_items
        )

        return verified_draft, claims_verifications
