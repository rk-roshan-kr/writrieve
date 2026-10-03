from .interface import DecisionAction, DecisionActionType

class DeterministicDecisionFallback:
    """
    Guaranteed deterministic fallback rule engine if the System-1 neural runtime encounters
    VRAM pressure, execution timeouts, or undefined states.
    """

    @classmethod
    def fallback_action(cls, step: int, default_source: str = "gmail") -> DecisionAction:
        if step == 0:
            return DecisionAction(
                action=DecisionActionType.QUERY_SOURCE,
                source=default_source,
                query="recent collaboration",
                reason="Initial cold start retrieval.",
                confidence=0.85
            )
        elif step == 1:
            return DecisionAction(
                action=DecisionActionType.QUERY_SOURCE,
                source="calendar",
                query="meeting conference",
                reason="Verifying temporal scheduling evidence.",
                confidence=0.88
            )
        else:
            return DecisionAction(
                action=DecisionActionType.STOP,
                reason="Deterministic fallback reached safe terminal cutoff.",
                confidence=0.80
            )
