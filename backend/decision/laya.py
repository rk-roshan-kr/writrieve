from typing import Optional
from backend.task.classifier import TaskRepresentation, TaskClass
from backend.task.requirements import InformationRequirement
from backend.evidence.state import EvidenceState
from backend.policy.budgets import RetrievalBudget
from .interface import DecisionAction, DecisionActionType

class LayaSystem1Controller:
    """
    Open-weight Laya System-1 Decision Controller.
    Takes (task, evidence_state, unknowns, budget, policy) and predicts
    the next bounded action in the control loop.
    Low latency, structured outputs, persistent tensor model in VRAM / fast fallback.
    """

    def __init__(self, use_cuda: bool = True):
        self.use_cuda = use_cuda

    def decide(
        self,
        task: TaskRepresentation,
        state: EvidenceState,
        budget: RetrievalBudget,
        requirements: list[InformationRequirement]
    ) -> DecisionAction:
        # 1. Check budget exhaustion
        if budget.is_exhausted():
            # If critical requirements met, STOP; else ABSTAIN
            if state.overall_sufficiency() >= 0.65:
                return DecisionAction(
                    action=DecisionActionType.STOP,
                    reason="Budget reached; sufficient partial evidence acquired for generation.",
                    confidence=0.88
                )
            return DecisionAction(
                action=DecisionActionType.ABSTAIN,
                reason="Budget limit reached without meeting mandatory evidence requirements.",
                confidence=0.45
            )

        # 2. Check for Ambiguous Entities (e.g. Class D)
        if task.task_class == TaskClass.CLASS_D_AMBIGUOUS and not task.target_entity:
            return DecisionAction(
                action=DecisionActionType.ASK_USER,
                reason="Target recipient is ambiguous with multiple competing candidates.",
                confidence=0.50,
                metadata={"question": "Multiple contacts match your query. Which one did you mean?"}
            )

        # 3. Check for Unresolved Conflicts
        if state.conflicts:
            unresolved = [c for c in state.conflicts if c.resolution_status == "UNRESOLVED"]
            if unresolved:
                return DecisionAction(
                    action=DecisionActionType.VERIFY_CONFLICT,
                    source="calendar",
                    query=f"{task.target_entity or ''} {unresolved[0].field}",
                    reason=f"Conflicting facts detected across sources for {unresolved[0].field}. Cross-verifying.",
                    confidence=0.92
                )

        # 4. Check Unfulfilled Mandatory Requirements
        unsatisfied = [r for r in requirements if not r.satisfied]

        if not unsatisfied or state.overall_sufficiency() >= 0.85:
            return DecisionAction(
                action=DecisionActionType.STOP,
                reason="All required evidence facets satisfied with high confidence. Proceeding to generation.",
                confidence=0.96
            )

        # 5. Iterative Query Selection based on current unsatisfied requirement
        next_req = unsatisfied[0]

        # Prioritize source not yet heavily used
        candidate_sources = [s for s in next_req.target_sources if s not in state.sources_used]
        chosen_source = candidate_sources[0] if candidate_sources else next_req.target_sources[0]

        # Build focused query
        query_terms = [task.target_entity or "", task.topic or "", task.event_context or ""]
        clean_query = " ".join([t for t in query_terms if t]).strip() or task.user_prompt

        if chosen_source in state.sources_used:
            return DecisionAction(
                action=DecisionActionType.REFINE_QUERY,
                source=chosen_source,
                query=f"{clean_query} follow-up",
                reason=f"Refining query on {chosen_source} to fulfill {next_req.name}.",
                confidence=0.90
            )

        return DecisionAction(
            action=DecisionActionType.QUERY_SOURCE,
            source=chosen_source,
            query=clean_query,
            reason=f"Need evidence of {next_req.name} from {chosen_source}.",
            confidence=0.93
        )
