import re
from typing import List, Dict, Any, Optional
from .state import EvidenceConflict
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class ConflictDetector:
    """
    Identifies factual discrepancies across heterogeneous personal sources.
    Example:
      - Calendar: "CCNCPS Conference: September 16"
      - LinkedIn: "Speaker at CCNCPS: September 18"
    Flags unresolved conflicts rather than silently averaging or guessing.
    """

    @classmethod
    def scan_for_conflicts(cls, items: List[ContextItem]) -> List[EvidenceConflict]:
        conflicts: List[EvidenceConflict] = []

        # 1. Date extraction for key events
        date_mentions: Dict[str, List[tuple]] = {}
        date_pattern = re.compile(r"\b(?:202[0-9]-[0-1][0-9]-[0-3][0-9]|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]* \d{1,2})\b", re.IGNORECASE)

        for item in items:
            matches = date_pattern.findall(item.content)
            for m in matches:
                norm_key = "conference_date" if "conference" in item.content.lower() or "ccncps" in item.content.lower() else "meeting_date"
                date_mentions.setdefault(norm_key, []).append((m, item.source, item.id))

        for field, entries in date_mentions.items():
            unique_dates = list(set(e[0] for e in entries))
            if len(unique_dates) > 1:
                mapping = {e[1]: f"{e[0]} (via {e[2]})" for e in entries}
                conflicts.append(EvidenceConflict(
                    field=field,
                    values=unique_dates,
                    source_mappings=mapping,
                    resolution_status="UNRESOLVED"
                ))

        return conflicts
