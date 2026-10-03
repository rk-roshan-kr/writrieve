import sys
import os
import pytest

# Ensure project root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.connectors.factory import get_context_provider

@pytest.fixture(scope="session")
def provider():
    return get_context_provider(force_provider="mock")
