import os
import time
from typing import Optional
from backend.writing.contract import WritingContract
from backend.writing.models.base import WritingModel, WritingOutput

try:
    from backend.generation.generation_runtime import OllamaGenerationModel
except ImportError:
    from generation.generation_runtime import OllamaGenerationModel

class RemoteOllamaWriter(WritingModel):
    """
    Remote / High-Parameter Writing Model (Qwen2.5:7b, Gemma, Mistral) accessed via Ollama or vLLM.
    """

    def __init__(self, model_name: str = "qwen2.5:7b"):
        super().__init__(model_name=model_name)
        self.ollama = OllamaGenerationModel(model=model_name)

    def generate(self, contract: WritingContract, revision_directive: Optional[str] = None) -> WritingOutput:
        start_time = time.time()
        prompt = contract.render_prompt_contract()
        if revision_directive:
            prompt += f"\n\nCRITICAL TARGETED REVISION DIRECTIVE:\n{revision_directive}\nRevise the draft to resolve the above issues."

        raw_draft = self.ollama.generate(prompt=prompt, context_evidence=[])
        latency_ms = (time.time() - start_time) * 1000
        tokens = len(raw_draft.split()) * 2

        return WritingOutput(
            draft=raw_draft.strip(),
            model_name=self.model_name,
            tokens_used=tokens,
            latency_ms=latency_ms
        )
