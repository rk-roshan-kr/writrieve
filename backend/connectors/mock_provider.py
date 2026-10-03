import os
import json
from typing import List, Dict, Any, Optional

try:
    from backend.models.schemas import ContextItem
    from backend.connectors.base import ContextProvider
except ImportError:
    from models.schemas import ContextItem
    from connectors.base import ContextProvider

class MockContextProvider(ContextProvider):
    """
    Mock Context Provider Adapter.
    Loads and normalizes structured personal context from:
    - mock_data/gmail.json (80 items)
    - mock_data/calendar.json (20 items)
    - mock_data/linkedin.json (30 items)
    - mock_data/drive.json (50 items)
    - mock_data/contacts.json (20 items)
    Total: 200 interconnected candidate signals.
    """

    def __init__(self, data_dir: Optional[str] = None):
        if not data_dir:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base, "data", "mock_data")
        self.data_dir = data_dir
        self._cache: Dict[str, ContextItem] = {}
        self._load_all()

    def _load_all(self):
        self._cache.clear()
        
        # 1. Gmail
        self._load_file("gmail.json", source="gmail", content_key="body", default_type="email")
        # 2. Calendar
        self._load_file("calendar.json", source="calendar", content_key="description", default_type="event")
        # 3. LinkedIn
        self._load_file("linkedin.json", source="linkedin", content_key="body", default_type="post")
        # 4. Drive
        self._load_file("drive.json", source="drive", content_key="body", default_type="doc")
        # 5. Contacts
        self._load_file("contacts.json", source="contacts", content_key="body", default_type="contact")

    def _load_file(self, filename: str, source: str, content_key: str, default_type: str):
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            return

        with open(filepath, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        for raw in raw_items:
            # Format content with subject or title if available
            title_part = raw.get("subject") or raw.get("title") or raw.get("name") or ""
            body_part = raw.get(content_key, "")
            formatted_content = f"{title_part}\n{body_part}".strip() if title_part else body_part

            item = ContextItem(
                id=raw.get("id"),
                source=source,
                type=raw.get("type", default_type),
                timestamp=raw.get("date", "2026-09-15T12:00:00"),
                people=raw.get("people", []),
                entities=raw.get("entities", []),
                content=formatted_content,
                reliability=raw.get("reliability", 0.90),
                permissions=raw.get("permissions", ["personal"]),
                provenance=raw.get("provenance", {})
            )
            self._cache[item.id] = item

    def get_all_candidates(self) -> List[ContextItem]:
        return list(self._cache.values())

    def get(self, item_id: str) -> Optional[ContextItem]:
        return self._cache.get(item_id)

    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[ContextItem]:
        q_lower = query.lower()
        results: List[ContextItem] = []
        for item in self._cache.values():
            if filters and "source" in filters and item.source != filters["source"]:
                continue
            if (q_lower in item.content.lower() or 
                any(q_lower in e.lower() for e in item.entities) or
                any(q_lower in p.lower() for p in item.people)):
                results.append(item)
        return results

    def capabilities(self) -> Dict[str, Any]:
        return {
            "provider": "MockContextProvider (Context Provider Adapter)",
            "status": "online",
            "is_mock": True,
            "connected_sources": ["gmail", "calendar", "linkedin", "drive", "contacts"],
            "total_signals": len(self._cache),
            "distribution": {
                "gmail": len([c for c in self._cache.values() if c.source == "gmail"]),
                "calendar": len([c for c in self._cache.values() if c.source == "calendar"]),
                "linkedin": len([c for c in self._cache.values() if c.source == "linkedin"]),
                "drive": len([c for c in self._cache.values() if c.source == "drive"]),
                "contacts": len([c for c in self._cache.values() if c.source == "contacts"]),
            }
        }
