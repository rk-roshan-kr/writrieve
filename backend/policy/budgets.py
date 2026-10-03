import time
from pydantic import BaseModel, Field

class RetrievalBudget(BaseModel):
    max_tool_calls: int = 8
    max_sources: int = 4
    max_items: int = 100
    max_context_tokens: int = 12000
    max_iterations: int = 3
    time_budget_ms: float = 8000.0

    # Dynamic tracking
    current_tool_calls: int = 0
    current_sources: int = 0
    current_items_retrieved: int = 0
    current_iterations: int = 0
    start_time: float = Field(default_factory=time.time)

    def is_exhausted(self) -> bool:
        if self.current_iterations >= self.max_iterations:
            return True
        if self.current_tool_calls >= self.max_tool_calls:
            return True
        if self.current_items_retrieved >= self.max_items:
            return True
        elapsed_ms = (time.time() - self.start_time) * 1000.0
        if elapsed_ms >= self.time_budget_ms:
            return True
        return False

    def record_iteration(self, tool_calls_in_iter: int, items_count: int):
        self.current_iterations += 1
        self.current_tool_calls += tool_calls_in_iter
        self.current_items_retrieved += items_count

    def budget_summary(self) -> dict:
        elapsed_ms = round((time.time() - self.start_time) * 1000.0, 1)
        return {
            "iterations": f"{self.current_iterations}/{self.max_iterations}",
            "tool_calls": f"{self.current_tool_calls}/{self.max_tool_calls}",
            "items_retrieved": f"{self.current_items_retrieved}/{self.max_items}",
            "elapsed_ms": elapsed_ms,
            "exhausted": self.is_exhausted()
        }
