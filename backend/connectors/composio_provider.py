import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from backend.models.schemas import ContextItem
    from backend.connectors.base import ContextProvider
    from backend.connectors.mock_provider import MockContextProvider
except ImportError:
    from models.schemas import ContextItem
    from connectors.base import ContextProvider
    from connectors.mock_provider import MockContextProvider

# Action registry decoupling Composio tool identifiers from core intelligence
COMPOSIO_ACTION_REGISTRY: Dict[str, Dict[str, str]] = {
    "gmail": {
        "search": "GMAIL_LIST_MESSAGES",
        "get": "GMAIL_FETCH_MESSAGE",
        "type": "email"
    },
    "calendar": {
        "search": "GOOGLECALENDAR_LIST_EVENTS",
        "get": "GOOGLECALENDAR_GET_EVENT",
        "type": "calendar_event"
    },
    "drive": {
        "search": "GOOGLEDRIVE_SEARCH_FILES",
        "get": "GOOGLEDRIVE_GET_FILE",
        "type": "document"
    },
    "github": {
        "search": "GITHUB_SEARCH_ISSUES_AND_PRS",
        "get": "GITHUB_GET_ISSUE",
        "type": "code_issue"
    }
}

# Forbidden mutating operations
FORBIDDEN_OPERATIONS = {"SEND", "DELETE", "UPDATE", "CREATE", "MODIFY", "TRASH", "DRAFT_SEND"}

class SecurityException(Exception):
    """Raised when an unauthorized mutating or unsafe tool call is attempted."""
    pass

class ComposioContextProvider(ContextProvider):
    """
    Production Composio Context Provider.
    Manages OAuth lifecycle, user-scoped authorized sessions, read-only enforcement,
    and normalization of heterogeneous data into canonical ContextItem records.
    """

    def __init__(self, user_id: str = "write4u_default_user", fixture_mode: bool = False):
        self.user_id = user_id
        self.api_key = os.getenv("COMPOSIO_API_KEY", "")
        self.client = None
        self.is_connected = False
        self.fixture_mode = fixture_mode

        self.fallback = MockContextProvider()

        if not self.fixture_mode and self.api_key:
            self._init_client()

    def _init_client(self):
        try:
            from composio import Composio
            self.client = Composio(api_key=self.api_key)
            self.is_connected = True
        except Exception as e:
            print(f"[ComposioProvider] SDK init deferred: {e}")
            self.is_connected = False

    def get_connection_link(self, app_name: str = "gmail", redirect_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates a secure user-scoped Composio Connect Link for OAuth authorization.
        The backend owns the identity relationship; browser only receives the redirect URL.
        """
        if not self.client:
            return {
                "success": False,
                "error": "Composio API key not configured or client offline",
                "connect_url": "https://app.composio.dev/"
            }

        try:
            auth_config_id = None
            if hasattr(self.client, "auth_configs"):
                configs = self.client.auth_configs.list()
                for item in getattr(configs, "items", []):
                    toolkit_slug = getattr(getattr(item, "toolkit", None), "slug", "")
                    if toolkit_slug.lower() == app_name.lower():
                        auth_config_id = item.id
                        break

            if not auth_config_id:
                auth_config_id = "ac_EeibxHb4fvkt"  # Known default for project

            link_kwargs = {"user_id": self.user_id, "auth_config_id": auth_config_id}
            if redirect_url:
                link_kwargs["callback_url"] = redirect_url

            req = self.client.connected_accounts.link(**link_kwargs)
            url = getattr(req, "redirect_url", getattr(req, "url", ""))
            return {
                "success": True,
                "connection_request_id": getattr(req, "id", None),
                "connect_url": url,
                "app": app_name,
                "user_id": self.user_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "connect_url": "https://app.composio.dev/"
            }

    def _enforce_read_only(self, action_name: str):
        action_upper = action_name.upper()
        for forbidden in FORBIDDEN_OPERATIONS:
            if forbidden in action_upper:
                raise SecurityException(
                    f"Write4U Security Guard blocked mutating action '{action_name}'. Write4U is strictly read-only."
                )

    def search(
        self,
        source: Optional[str] = None,
        query: str = "",
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ContextItem]:
        """
        Executes read-only search across authorized Composio toolkits for the requested source.
        Supports: 'gmail', 'calendar', 'drive', 'github', or 'all'.
        """
        if source is None:
            source = (filters or {}).get("source", "all")
        elif filters and "source" in filters and source not in COMPOSIO_ACTION_REGISTRY and source != "all":
            actual_query = source
            source = filters["source"]
            query = actual_query

        # If fixture mode is explicitly enabled (automated tests), load strictly from tests/fixtures
        if self.fixture_mode:
            return self._load_fixtures(source, query)

        if not self.client:
            return []

        results: List[ContextItem] = []
        sources_to_query = [source] if source in COMPOSIO_ACTION_REGISTRY else (
            list(COMPOSIO_ACTION_REGISTRY.keys()) if source == "all" else ["gmail"]
        )

        for src in sources_to_query:
            action_info = COMPOSIO_ACTION_REGISTRY.get(src)
            if not action_info:
                continue

            action_name = action_info["search"]
            self._enforce_read_only(action_name)

            try:
                # Support both modern c.tools.execute and legacy c.actions.execute
                res = None
                if hasattr(self.client, "tools") and hasattr(self.client.tools, "execute"):
                    res = self.client.tools.execute(
                        slug=action_name,
                        arguments={"query": query, "max_results": 10},
                        user_id=self.user_id
                    )
                elif hasattr(self.client, "actions") and hasattr(self.client.actions, "execute"):
                    res = self.client.actions.execute(
                        action=action_name,
                        params={"query": query, "max_results": 10},
                        entity_id=self.user_id
                    )

                if res:
                    raw_items = self._extract_raw_list(src, res)
                    for raw in raw_items:
                        item = self._normalize_item(src, raw)
                        if item:
                            results.append(item)
            except Exception as e:
                print(f"[ComposioProvider] Tool execution error on {src}: {e}")

        # Fall back to fixture mode if enabled or to deterministic fallback provider
        if not results:
            if self.fixture_mode:
                return self._load_fixtures(source, query)
            if self.fallback:
                return self.fallback.search(source=source, query=query, filters=filters)

        return results

    def get(self, source: str, item_id: str) -> Optional[ContextItem]:
        """Fetch a specific item by unique ID from Composio."""
        if self.fixture_mode:
            for item in self._load_fixtures(source, ""):
                if item.id == item_id:
                    return item
            return None

        if not self.client:
            return None

        action_info = COMPOSIO_ACTION_REGISTRY.get(source)
        if not action_info:
            return None

        action_name = action_info["get"]
        self._enforce_read_only(action_name)

        try:
            if hasattr(self.client, "actions") and hasattr(self.client.actions, "execute"):
                res = self.client.actions.execute(
                    action=action_name,
                    params={"id": item_id},
                    entity_id=self.user_id
                )
                return self._normalize_item(source, res.get("data", {}))
        except Exception:
            return None
        return None

    def _extract_raw_list(self, source: str, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = response.get("data", {}) if isinstance(response, dict) else {}
        if source == "gmail":
            return data.get("messages", [])
        elif source == "calendar":
            return data.get("events", [])
        elif source == "drive":
            return data.get("files", [])
        elif source == "github":
            return data.get("items", [])
        return []

    def _normalize_item(self, source: str, raw: Dict[str, Any]) -> Optional[ContextItem]:
        """
        Normalizes vendor-specific payload into canonical ContextItem with audit provenance.
        """
        retrieved_at = datetime.now(timezone.utc).isoformat()
        raw_id = str(raw.get("id", "unknown"))

        if source == "gmail":
            subject = raw.get("subject", "No Subject")
            from_addr = raw.get("from", "")
            snippet = raw.get("snippet", raw.get("body", ""))
            return ContextItem(
                id=f"gmail_{raw_id}",
                source="gmail",
                type="email",
                timestamp=raw.get("date", retrieved_at),
                people=[from_addr] if from_addr else [],
                entities=[subject] if subject else [],
                content=f"Subject: {subject}\n{snippet}".strip(),
                reliability=0.98,
                provenance={
                    "provider": "composio",
                    "source_id": raw_id,
                    "authorized_user": self.user_id,
                    "retrieved_at": retrieved_at
                }
            )

        elif source == "calendar":
            summary = raw.get("summary", "Calendar Event")
            start = raw.get("start", {}).get("dateTime", retrieved_at)
            description = raw.get("description", "")
            attendees = [a.get("displayName", a.get("email", "")) for a in raw.get("attendees", []) if isinstance(a, dict)]
            return ContextItem(
                id=f"calendar_{raw_id}",
                source="calendar",
                type="calendar_event",
                timestamp=start,
                people=attendees,
                entities=[summary],
                content=f"Event: {summary}\n{description}".strip(),
                reliability=0.95,
                provenance={
                    "provider": "composio",
                    "source_id": raw_id,
                    "authorized_user": self.user_id,
                    "retrieved_at": retrieved_at
                }
            )

        elif source == "drive":
            name = raw.get("name", "Document")
            snippet = raw.get("snippet", "")
            return ContextItem(
                id=f"drive_{raw_id}",
                source="drive",
                type="document",
                timestamp=raw.get("modifiedTime", retrieved_at),
                people=[],
                entities=[name],
                content=f"Document: {name}\n{snippet}".strip(),
                reliability=0.92,
                provenance={
                    "provider": "composio",
                    "source_id": raw_id,
                    "authorized_user": self.user_id,
                    "retrieved_at": retrieved_at
                }
            )

        return None

    def _load_fixtures(self, source: str, query: str) -> List[ContextItem]:
        """Loads canonical test fixtures strictly for offline testing."""
        fixtures_dir = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"
        items: List[ContextItem] = []

        if source in ["gmail", "all"]:
            p = fixtures_dir / "gmail_response.json"
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    for raw in json.load(f).get("messages", []):
                        item = self._normalize_item("gmail", raw)
                        if item and (not query or query.lower() in item.content.lower()):
                            items.append(item)

        if source in ["calendar", "all"]:
            p = fixtures_dir / "calendar_response.json"
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    for raw in json.load(f).get("events", []):
                        item = self._normalize_item("calendar", raw)
                        if item and (not query or query.lower() in item.content.lower()):
                            items.append(item)

        if source in ["drive", "all"]:
            p = fixtures_dir / "drive_response.json"
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    for raw in json.load(f).get("files", []):
                        item = self._normalize_item("drive", raw)
                        if item and (not query or query.lower() in item.content.lower()):
                            items.append(item)

        return items

    def get_all_candidates(self) -> List[ContextItem]:
        """Returns candidate pool from fallback signals or fixtures."""
        if self.fallback:
            return self.fallback.get_all_candidates()
        return self._load_fixtures("all", "")

    def capabilities(self) -> Dict[str, Any]:
        return {
            "provider": "ComposioContextProvider",
            "is_connected": self.is_connected,
            "user_id": self.user_id,
            "connected_toolkits": list(COMPOSIO_ACTION_REGISTRY.keys()),
            "security": "Strictly Read-Only (Mutations Blocked)",
            "fixture_mode": self.fixture_mode
        }

