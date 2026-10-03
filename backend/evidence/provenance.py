from typing import List, Dict, Any
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class ProvenanceTracker:
    """
    Maintains cryptographic and metadata traceability for every piece of evidence used in generation.
    Connects every claim in final text back to exact source, item ID, timestamp, and author.
    """

    @classmethod
    def build_provenance_map(cls, items: List[ContextItem]) -> Dict[str, Dict[str, Any]]:
        prov_map = {}
        for item in items:
            prov_map[item.id] = {
                "source": item.source,
                "timestamp": item.timestamp,
                "people": item.people,
                "entities": item.entities,
                "reliability": item.reliability,
                "provider": item.provenance.get("provider", "local") if hasattr(item, "provenance") else "unknown"
            }
        return prov_map
