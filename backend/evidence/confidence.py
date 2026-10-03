from typing import List, Dict
from backend.task.requirements import InformationRequirement
from .state import EvidenceState

class ConfidenceEstimator:
    """
    Computes probabilistic confidence scores across required task facets
    (e.g., recipient_identity: 0.98, prior_interaction: 0.94, topic_context: 0.97).
    """

    @classmethod
    def evaluate(cls, state: EvidenceState, requirements: List[InformationRequirement]) -> Dict[str, float]:
        scores = {}
        for req in requirements:
            # Check if any evidence item matches target sources or topics
            matching_items = [
                item for item in state.items
                if item.source in req.target_sources
            ]
            if not matching_items:
                scores[req.name] = 0.1
                req.satisfied = False
            else:
                # Base score derived from item reliability and count
                avg_rel = sum(it.reliability for it in matching_items) / len(matching_items)
                score = min(0.99, round(avg_rel * (0.8 + 0.05 * len(matching_items)), 2))
                scores[req.name] = score
                req.satisfied = (score >= 0.75)
                req.evidence_item_ids = [it.id for it in matching_items]
                req.confidence = score

        return scores
