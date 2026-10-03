from typing import Tuple, List
from backend.evidence.state import EvidenceState, TerminalStatus
from backend.policy.budgets import RetrievalBudget
from backend.task.requirements import InformationRequirement

class StoppingController:
    """
    Evaluates whether the acquisition loop should terminate or continue.
    Evaluates sufficiency, budget consumption, and required interactions.
    """

    @classmethod
    def evaluate(
        cls,
        state: EvidenceState,
        budget: RetrievalBudget,
        requirements: List[InformationRequirement]
    ) -> Tuple[bool, TerminalStatus, str]:
        # 1. Check if all mandatory requirements satisfied
        all_mand_satisfied = all(r.satisfied for r in requirements if r.mandatory)
        overall_conf = state.overall_sufficiency()

        if all_mand_satisfied and overall_conf >= 0.80:
            return True, TerminalStatus.SUCCESS, "All mandatory evidence requirements satisfied with high confidence."

        # 2. Check if budget exhausted
        if budget.is_exhausted():
            if overall_conf >= 0.60:
                return True, TerminalStatus.PARTIAL, "Retrieval budget exhausted; sufficient evidence for partial draft."
            else:
                return True, TerminalStatus.ABSTAIN, "Budget exhausted without satisfying mandatory context facets."

        # 3. Check for blocking unknowns or ambiguities
        if "Multiple people named Rahul" in state.unknowns or any("ambiguity" in u.lower() for u in state.unknowns):
            return True, TerminalStatus.ASK_USER, "Entity resolution is ambiguous; user clarification required."

        # Continue acquisition loop
        return False, TerminalStatus.ACQUIRING, "Continuing iterative evidence acquisition."
