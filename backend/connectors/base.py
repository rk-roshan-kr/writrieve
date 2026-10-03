from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class ContextProvider(ABC):
    """
    Abstract Canonical Context Provider Contract.
    Enforces a unified search and retrieval interface across all sources
    (Composio personal sources, Public Web, Long-Term Memory).
    """

    @abstractmethod
    def search(
        self,
        source: Optional[str] = None,
        query: str = "",
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ContextItem]:
        """
        Search for canonical ContextItem records across a specified source.
        Args:
            source: Source identifier (e.g. 'gmail', 'calendar', 'drive', 'github', 'web', 'memory', 'all')
            query: Free-text search query
            filters: Optional dictionary of domain filters
        """
        pass

    @abstractmethod
    def get(self, source: str, item_id: str) -> Optional[ContextItem]:
        """Fetch a specific canonical ContextItem by source and unique ID."""
        pass

    @abstractmethod
    def get_all_candidates(self) -> List[ContextItem]:
        """Return the complete available candidate signal pool."""
        pass

    @abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        """Return provider type, connected sources, and live status."""
        pass
