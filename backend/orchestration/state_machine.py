from backend.evidence.state import TerminalStatus

class StateMachine:
    """
    Explicit finite state machine governing the Write4U iterative acquisition cycle.
    Transitions:
      INITIALIZING -> ACQUIRING
      ACQUIRING -> ACQUIRING (loop)
      ACQUIRING -> SUCCESS (sufficiency >= threshold)
      ACQUIRING -> PARTIAL (budget cutoff with partial evidence)
      ACQUIRING -> ASK_USER (unresolved entity ambiguity or permission needs)
      ACQUIRING -> ABSTAIN (insufficient evidence to safely proceed)
      ACQUIRING -> FAILED (connector/broker fatal failure)
    """

    ALLOWED_TRANSITIONS = {
        TerminalStatus.INITIALIZING: {TerminalStatus.ACQUIRING, TerminalStatus.ASK_USER, TerminalStatus.ABSTAIN},
        TerminalStatus.ACQUIRING: {
            TerminalStatus.ACQUIRING,
            TerminalStatus.SUCCESS,
            TerminalStatus.PARTIAL,
            TerminalStatus.ASK_USER,
            TerminalStatus.ABSTAIN,
            TerminalStatus.FAILED
        },
        TerminalStatus.SUCCESS: set(),
        TerminalStatus.PARTIAL: set(),
        TerminalStatus.ASK_USER: set(),
        TerminalStatus.ABSTAIN: set(),
        TerminalStatus.FAILED: set()
    }

    @classmethod
    def can_transition(cls, current: TerminalStatus, next_status: TerminalStatus) -> bool:
        return next_status in cls.ALLOWED_TRANSITIONS.get(current, set())
