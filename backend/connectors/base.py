from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class ContextProvider(ABC):
    """
    Abstract Context Provider Adapter.
    Enforces a canonical interface whether pulling from local mock JSON datasets
    or a live Happenstance MCP / external provider.
    """

    @abstractmethod
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[ContextItem]:
        """Search across connected digital sources returning canonical ContextItem records."""
        pass

    @abstractmethod
    def get(self, item_id: str) -> Optional[ContextItem]:
        """Fetch a specific canonical ContextItem by unique ID."""
        pass

    @abstractmethod
    def get_all_candidates(self) -> List[ContextItem]:
        """Return the complete available candidate signal pool."""
        pass

    @abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        """Return provider type, connected sources, and live status."""
        pass
