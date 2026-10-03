from backend.connectors.factory import get_context_provider
from backend.connectors.mock_provider import MockContextProvider
from backend.connectors.happenstance import HappenstanceMCPProvider

def test_mock_provider_loading():
    provider = MockContextProvider()
    caps = provider.capabilities()

    assert caps["total_signals"] == 200
    assert caps["distribution"]["gmail"] == 80
    assert caps["distribution"]["calendar"] == 20
    assert caps["distribution"]["linkedin"] == 30
    assert caps["distribution"]["drive"] == 50
    assert caps["distribution"]["contacts"] == 20

def test_mock_provider_search():
    provider = MockContextProvider()
    results = provider.search("FieldChain")
    assert len(results) > 0
    assert all("fieldchain" in r.content.lower() or any("fieldchain" in e.lower() for e in r.entities) for r in results)

def test_happenstance_fallback():
    # Unauthenticated / offline Happenstance should safely fallback
    mcp_provider = HappenstanceMCPProvider(mcp_url="http://invalid-host:9999")
    assert mcp_provider.is_connected is False
    candidates = mcp_provider.get_all_candidates()
    assert len(candidates) == 200
