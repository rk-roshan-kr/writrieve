from typing import Dict, Any
from pydantic import BaseModel

class WriterBenchmarkScore(BaseModel):
    model_name: str
    factual_fidelity: float         # F (0.0 to 1.0)
    style_similarity: float         # S (0.0 to 1.0)
    grounding: float                # G (0.0 to 1.0)
    constraint_satisfaction: float # C (0.0 to 1.0)
    naturalness: float              # N (0.0 to 1.0)
    latency_ms: float
    latency_score: float            # L (0.0 to 1.0)
    composite_score: float          # W

def evaluate_writer_performance(
    model_name: str,
    factual_fidelity: float,
    style_similarity: float,
    grounding: float,
    constraint_satisfaction: float,
    naturalness: float,
    latency_ms: float
) -> WriterBenchmarkScore:
    """
    Computes Write4U Writer Shootout Score:
    W = 0.25*F + 0.20*S + 0.20*G + 0.15*C + 0.10*N + 0.10*L
    """
    # L normalized: <=200ms gives 1.0, 2000ms gives 0.0
    latency_score = max(0.0, min(1.0, 1.0 - (latency_ms / 2000.0)))

    composite_w = (
        0.25 * factual_fidelity +
        0.20 * style_similarity +
        0.20 * grounding +
        0.15 * constraint_satisfaction +
        0.10 * naturalness +
        0.10 * latency_score
    )

    return WriterBenchmarkScore(
        model_name=model_name,
        factual_fidelity=factual_fidelity,
        style_similarity=style_similarity,
        grounding=grounding,
        constraint_satisfaction=constraint_satisfaction,
        naturalness=naturalness,
        latency_ms=latency_ms,
        latency_score=latency_score,
        composite_score=round(composite_w, 4)
    )
