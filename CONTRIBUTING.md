# Contributing to Write4U ✦

Thank you for your interest in contributing to **Write4U**! We are building an open-weight, privacy-first context orchestration engine, and we welcome contributions from the community.

---

## 🛠️ Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/write4u/write4u.git
   cd write4u
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   pip install pytest httpx ruff
   ```

4. **Run the Test Suite**:
   ```bash
   pytest -v
   ```

5. **Start the Local Engine**:
   ```bash
   python -m uvicorn backend.main:app --reload
   ```

---

## 🔌 How to Add a New Context Provider Adapter

Write4U relies on the **Context Provider Adapter Pattern** to decouple digital sources from the core Context Engine.

To add a new provider (e.g., Notion, Obsidian, Slack, or a custom MCP server):

1. Create a new file in `backend/connectors/your_provider.py`.
2. Inherit from `ContextProvider` in `backend/connectors/base.py`:
   ```python
   from backend.connectors.base import ContextProvider
   from backend.models.schemas import ContextItem

   class NotionContextProvider(ContextProvider):
       def search(self, query: str, filters=None) -> list[ContextItem]:
           ...

       def get(self, item_id: str) -> ContextItem | None:
           ...

       def get_all_candidates(self) -> list[ContextItem]:
           ...

       def capabilities(self) -> dict:
           return {"provider": "NotionContextProvider", "status": "online"}
   ```
3. Register your provider in `backend/connectors/factory.py`.
4. Add unit tests in `tests/test_providers.py`.

---

## 🧠 Connecting Open-Weight Models (Ollama, vLLM, Local)

Write4U is designed open-weight first. You can easily connect local models:

* **Ollama**:
  ```bash
  ollama run qwen2.5:8b
  ```
  Set in your `.env`:
  ```env
  LLM_PROVIDER=open_weights
  LLM_MODEL=qwen2.5:8b
  LLM_ENDPOINT=http://localhost:11434
  ```

* **vLLM**:
  ```bash
  vllm serve Qwen/Qwen2.5-8B-Instruct --port 8000
  ```

---

## 🧪 Testing Guidelines

Before submitting a Pull Request, ensure that:
1. All tests pass: `pytest -v`
2. The empirical benchmark executes without errors: `python evaluation/benchmark.py`
3. Any new schemas maintain backwards compatibility with the canonical `ContextItem` schema.

---

## 📜 Pull Request Process

1. Fork the repo and create a new feature branch (`git checkout -b feat/my-new-connector`).
2. Commit your changes with clear, descriptive commit messages.
3. Push to your branch and open a Pull Request.
4. CI checks will automatically validate test suites across Python 3.10, 3.11, and 3.12.
