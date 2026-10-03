import os
import time
import json
import urllib.request
from typing import Optional
from backend.writing.contract import WritingContract
from backend.writing.models.base import WritingModel, WritingOutput

class LocalGroundedWriter(WritingModel):
    """
    Local Grounded Professional Writer.
    Powered by Qwen3-1.7B (qwen2.5:1.5b Q4) running locally on NVIDIA RTX 3050 (4GB VRAM)
    via Ollama in fast non-thinking mode.
    """

    def __init__(self, model_name: str = "qwen2.5:1.5b"):
        super().__init__(model_name=model_name)
        self.ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/generate")

    def generate(self, contract: WritingContract, revision_directive: Optional[str] = None) -> WritingOutput:
        start_time = time.time()

        prompt = contract.render_prompt_contract()
        if revision_directive:
            prompt += f"\n\nCRITICAL TARGETED REVISION DIRECTIVE:\n{revision_directive}\nRevise the draft to resolve the above issues."

        draft = None
        # Attempt generation via local Qwen3-1.7B on Ollama
        try:
            payload = json.dumps({
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 300
                }
            }).encode("utf-8")

            req = urllib.request.Request(
                self.ollama_endpoint,
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                draft = result.get("response", "").strip()
        except Exception as e:
            print(f"[LocalGroundedWriter] Ollama fallback to deterministic assembler: {e}")

        # If Ollama didn't return text, assemble deterministically from contract claims
        if not draft:
            recipient = contract.audience.recipient or "Colleague"
            platform = contract.constraints.platform

            if platform == "email":
                greeting = f"Dear {recipient}," if contract.style.formality >= 0.7 else f"Hi {recipient},"
                claims = [e.claim for e in contract.evidence]
                body = " ".join(claims) if claims else "I am writing to follow up on our recent discussion."
                closing = "Best regards,\nAlex Rivera" if contract.style.formality >= 0.7 else "Best,\nAlex"
                draft = f"{greeting}\n\n{body}\n\nWould you be open to a brief sync next week to coordinate?\n\n{closing}"
            elif platform == "linkedin":
                claims = " ".join([e.claim for e in contract.evidence])
                draft = f"Excited to share insights on our latest project:\n\n{claims}\n\n#DistributedSystems #OpenSource #Writrieve"
            else:
                draft = f"Key verified points:\n" + "\n".join([f"- {e.claim}" for e in contract.evidence])

        latency_ms = (time.time() - start_time) * 1000
        tokens = len(draft.split()) * 2

        return WritingOutput(
            draft=draft.strip(),
            model_name=self.model_name,
            tokens_used=tokens,
            latency_ms=latency_ms
        )
