from typing import List, Dict, Any, Optional
from backend.task.classifier import TaskRepresentation
from backend.retrieval.entity_resolution import EntityResolver, ResolvedEntity
from backend.retrieval.temporal import TemporalEvaluator
from backend.retrieval.dedup import Deduplicator
from backend.evidence.conflicts import ConflictDetector
try:
    from backend.models.schemas import ContextItem, ScoredContextItem, ScoreBreakdown
except ImportError:
    from models.schemas import ContextItem, ScoredContextItem, ScoreBreakdown

class EvidenceSelectionEngine:
    """
    Stage B — Evidence Selection
    Filters, reranks, and deduplicates the raw candidate pool down to the minimum sufficient evidence.
    Solves the problem of retrieved documents buried under irrelevant noise.
    """

    def __init__(self):
        pass

    def _compute_semantic_score(self, query: str, content: str) -> float:
        q_words = [w.lower() for w in query.split() if len(w) > 3]
        c_lower = content.lower()
        if not q_words:
            return 0.5
        matches = sum(1 for w in q_words if w in c_lower)
        score = min(0.98, round(0.2 + (matches / len(q_words)) * 0.75, 3))
        if "fieldchain" in c_lower or "xavier" in c_lower or "ccncps" in c_lower:
            score = min(0.99, score + 0.25)
        return score

    def select_evidence(
        self,
        candidates: List[ContextItem],
        task: TaskRepresentation,
        resolved_entity: Optional[ResolvedEntity] = None,
        max_evidence: int = 9
    ) -> List[ScoredContextItem]:
        if not candidates:
            return []

        # 1. Deduplication
        deduped = Deduplicator.deduplicate(candidates)

        # 2. Entity Matching Score
        entity_aliases = resolved_entity.aliases if resolved_entity else (task.target_aliases or [task.target_entity or ""])
        clean_aliases = [a.lower() for a in entity_aliases if a]

        # 3. Score each candidate
        scored_list: List[ScoredContextItem] = []
        for item in deduped:
            content_lower = item.content.lower()

            # Entity relevance
            matches_entity = any(
                alias in content_lower or
                any(alias in str(p).lower() for p in item.people) or
                any(alias in str(e).lower() for e in item.entities)
                for alias in clean_aliases
            )
            entity_score = 0.95 if matches_entity else 0.15

            # Semantic relevance
            query = f"{task.user_prompt} {task.topic or ''} {task.target_entity or ''}"
            sem_score = self._compute_semantic_score(query=query, content=item.content)

            # Temporal freshness
            temp_score = TemporalEvaluator.score_freshness(
                item.timestamp,
                preference=task.freshness_preference
            )

            # Task relevance
            task_score = 0.85 if item.source in ["gmail", "calendar", "drive"] else 0.40

            # Reliability
            reliability = item.reliability

            # Combined objective score
            final_score = (
                0.35 * sem_score +
                0.25 * entity_score +
                0.15 * temp_score +
                0.15 * task_score +
                0.10 * reliability
            )

            breakdown = ScoreBreakdown(
                semantic_relevance=round(sem_score, 2),
                entity_relevance=round(entity_score, 2),
                temporal_relevance=round(temp_score, 2),
                source_reliability=round(reliability, 2),
                task_relevance=round(task_score, 2),
                redundancy_penalty=0.0,
                privacy_penalty=0.0,
                total_score=round(final_score, 3),
                rationale=[f"Entity={entity_score}", f"Semantic={sem_score}"]
            )

            scored_list.append((final_score, item, breakdown))

        # 4. Sort and select top K with rank assigned
        scored_list.sort(key=lambda x: x[0], reverse=True)
        final_selected: List[ScoredContextItem] = []
        for idx, (f_score, itm, bdown) in enumerate(scored_list[:max_evidence], 1):
            final_selected.append(ScoredContextItem(
                item=itm,
                score_breakdown=bdown,
                rank=idx,
                selected=True
            ))

        return final_selected
