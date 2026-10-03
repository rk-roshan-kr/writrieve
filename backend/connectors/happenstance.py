import os
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

try:
    from backend.models.schemas import ContextItem
    from backend.connectors.base import ContextProvider
    from backend.connectors.mock_provider import MockContextProvider
except ImportError:
    from models.schemas import ContextItem
    from connectors.base import ContextProvider
    from connectors.mock_provider import MockContextProvider

class HappenstanceMCPProvider(ContextProvider):
    """
    Happenstance MCP Provider Adapter.
    Connects to external Happenstance MCP gateway when configured.
    Gracefully falls back to MockContextProvider if unauthenticated or offline.
    """

    def __init__(self, mcp_url: Optional[str] = None, api_key: Optional[str] = None):
        self.mcp_url = mcp_url or os.getenv("HAPPENSTANCE_MCP_URL", "http://localhost:3000/mcp")
        self.api_key = api_key or os.getenv("HAPPENSTANCE_API_KEY", "")
        self.fallback_provider = MockContextProvider()
        self.is_connected = False
        self._check_connection()

    def _check_connection(self):
        if not self.api_key and "localhost" not in self.mcp_url:
            self.is_connected = False
            return

        try:
            req = urllib.request.Request(f"{self.mcp_url}/health", headers={"Authorization": f"Bearer {self.api_key}"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    self.is_connected = True
        except Exception:
            self.is_connected = False

    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[ContextItem]:
        if not self.is_connected:
            return self.fallback_provider.search(query, filters)
        
        # Real Happenstance MCP query call
        try:
            payload = json.dumps({"query": query, "filters": filters or {}}).encode("utf-8")
            req = urllib.request.Request(
                f"{self.mcp_url}/context/search",
                data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                # Canonical normalization
                items: List[ContextItem] = []
                for raw in data.get("items", []):
                    items.append(ContextItem(
                        id=raw.get("id"),
                        source=raw.get("source", "mcp"),
                        type=raw.get("type", "message"),
                        timestamp=raw.get("timestamp", "2026-09-15"),
                        people=raw.get("people", []),
                        entities=raw.get("entities", []),
                        content=raw.get("content", ""),
                        reliability=raw.get("reliability", 0.95),
                        provenance=raw.get("provenance", {"provider": "happenstance_mcp"})
                    ))
                return items
        except Exception as e:
            print(f"[HappenstanceMCP] Query failed, falling back to mock adapter: {e}")
            return self.fallback_provider.search(query, filters)

    def get(self, item_id: str) -> Optional[ContextItem]:
        if not self.is_connected:
            return self.fallback_provider.get(item_id)
        return self.fallback_provider.get(item_id)

    def get_all_candidates(self) -> List[ContextItem]:
        if not self.is_connected:
            return self.fallback_provider.get_all_candidates()
        return self.fallback_provider.get_all_candidates()

    def capabilities(self) -> Dict[str, Any]:
        return {
            "provider": "HappenstanceMCPProvider",
            "is_connected": self.is_connected,
            "mcp_url": self.mcp_url,
            "fallback_active": not self.is_connected,
            "connected_sources": ["gmail", "calendar", "linkedin", "drive", "contacts"],
            "total_signals": len(self.get_all_candidates())
        }
