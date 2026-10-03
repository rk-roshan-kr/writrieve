import hashlib
import re
from typing import List, Set
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class Deduplicator:
    """
    Eliminates near-duplicate items across email threads, calendar invites, and draft revisions.
    """

    @classmethod
    def deduplicate(cls, items: List[ContextItem], similarity_threshold: float = 0.85) -> List[ContextItem]:
        seen_hashes: Set[str] = set()
        unique_items: List[ContextItem] = []

        for item in items:
            # Normalize content by removing whitespace and non-alphanumeric chars
            norm_content = re.sub(r"\W+", "", item.content.lower())[:200]
            content_hash = hashlib.md5(norm_content.encode("utf-8")).hexdigest()

            if content_hash in seen_hashes:
                continue

            seen_hashes.add(content_hash)
            unique_items.append(item)

        return unique_items
