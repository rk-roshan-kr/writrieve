from typing import Tuple
from backend.task.classifier import TaskRepresentation, TaskClass

class RiskEvaluator:
    """
    Evaluates policy risk level (low, medium, high) based on user prompt,
    target recipients, and sensitive domain triggers.
    """

    @classmethod
    def evaluate(cls, task: TaskRepresentation) -> Tuple[str, str]:
        if task.task_class == TaskClass.CLASS_E_SENSITIVE:
            return "high", "Task involves financial, legal, or highly sensitive credentials."
        if task.task_class == TaskClass.CLASS_D_AMBIGUOUS and not task.target_entity:
            return "medium", "Target entity has multiple conflicting candidates; confirmation advised."
        return "low", "Standard professional drafting and context lookup."
