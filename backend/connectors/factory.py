import os
from typing import Optional
try:
    from backend.connectors.base import ContextProvider
    from backend.connectors.mock_provider import MockContextProvider
    from backend.connectors.happenstance import HappenstanceMCPProvider
    from backend.connectors.composio_provider import ComposioContextProvider
except ImportError:
    from connectors.base import ContextProvider
    from connectors.mock_provider import MockContextProvider
    from connectors.happenstance import HappenstanceMCPProvider
    from connectors.composio_provider import ComposioContextProvider

_instance: Optional[ContextProvider] = None

def get_context_provider(force_provider: Optional[str] = None) -> ContextProvider:
    """
    Factory function returning the active ContextProvider.
    Supports:
    - 'composio' (Composio OAuth & MCP session adapter)
    - 'happenstance' (Happenstance MCP adapter)
    - 'mock' (Deterministic local 200 signal dataset)
    """
    global _instance
    if _instance is not None and not force_provider:
        return _instance

    mode = force_provider or os.getenv("CONTEXT_PROVIDER", "").lower()

    if mode == "composio" or os.getenv("COMPOSIO_API_KEY"):
        _instance = ComposioContextProvider()
    elif mode == "happenstance" or os.getenv("HAPPENSTANCE_API_KEY"):
        _instance = HappenstanceMCPProvider()
    else:
        _instance = MockContextProvider()

    return _instance
