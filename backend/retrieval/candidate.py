from typing import List, Dict, Any, Optional
from backend.policy.budgets import RetrievalBudget
from backend.policy.permissions import PolicyPermissions
try:
    from backend.models.schemas import ContextItem
    from backend.connectors.factory import get_context_provider
except ImportError:
    from models.schemas import ContextItem
    from connectors.factory import get_context_provider

class CandidateDiscoveryBroker:
    """
    Stage A — Candidate Discovery
    Executes cheap initial candidate retrieval from specified personal connectors
    (Gmail, Calendar, Drive, GitHub, LinkedIn) under strict budget and permission boundaries.
    """

    def __init__(self, user_id: str = "write4u_default_user"):
        self.user_id = user_id
        self.provider = get_context_provider()

    def discover_candidates(
        self,
        source: str,
        query: str,
        budget: RetrievalBudget,
        limit: int = 35
    ) -> List[ContextItem]:
        # Enforce source permissions
        allowed_sources = PolicyPermissions.filter_allowed_sources({source})
        if not allowed_sources:
            return []

        # Check budget limits
        if budget.is_exhausted():
            return []

        # Query provider
        candidates = self.provider.search(query=query, filters={"source": source})
        sliced = candidates[:limit]

        # Record in budget
        budget.record_iteration(tool_calls_in_iter=1, items_count=len(sliced))

        return sliced
