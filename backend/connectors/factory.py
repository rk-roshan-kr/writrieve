import os
from typing import Optional

try:
    from backend.connectors.base import ContextProvider
    from backend.connectors.mock_provider import MockContextProvider
    from backend.connectors.happenstance import HappenstanceMCPProvider
except ImportError:
    from connectors.base import ContextProvider
    from connectors.mock_provider import MockContextProvider
    from connectors.happenstance import HappenstanceMCPProvider

_instance: Optional[ContextProvider] = None

def get_context_provider(force_provider: Optional[str] = None) -> ContextProvider:
    """
    Factory function returning the active ContextProvider.
    Defaults to MockContextProvider unless HAPPENSTANCE_API_KEY is present
    or force_provider == 'happenstance'.
    """
    global _instance
    if _instance is not None and not force_provider:
        return _instance

    mode = force_provider or os.getenv("CONTEXT_PROVIDER", "mock").lower()

    if mode == "happenstance" or os.getenv("HAPPENSTANCE_API_KEY"):
        _instance = HappenstanceMCPProvider()
    else:
        _instance = MockContextProvider()

    return _instance
