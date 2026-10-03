# Write4U — Task-Aware Personal Context Engine ✦

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Decision Model](https://img.shields.io/badge/System--1-Laya%20421M%20(Apache--2.0)-green.svg)](backend/planner/laya_decision.py)
[![Connectors](https://img.shields.io/badge/Connectors-Composio%20MCP%20%7C%20Managed%20OAuth-purple.svg)](backend/connectors/composio_provider.py)
[![Manifest V3](https://img.shields.io/badge/Chrome%20Extension-Manifest%20V3-success.svg)](extension/manifest.json)

> **Write4U is a task-aware personal context engine where an open-weight System-1 decision model (Laya) determines what context to retrieve, Composio provides authenticated access to the user's digital sources, a context-selection engine identifies the minimum sufficient evidence, and an open-weight LLM generates the final grounded response.**

Writing is the first application. Write4U runs right inside your browser (Gmail, LinkedIn, GitHub, or any web composer) via a native Chrome extension without blindly dumping hundreds of private messages into an LLM.

---

## 🏛️ The Five Major Layers

```
                         ┌───────────────────────┐
                         │         USER          │
                         │ "Write a follow-up to │
                         │  Prof. X on research" │
                         └───────────┬───────────┘
                                     │
                                     ▼
                    ┌────────────────────────────┐
                    │  LAYER 1: BROWSER EXTENSION│
                    │  Active page, recipient,   │
                    │  thread ID & user task     │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │      FASTAPI BACKEND       │
                    │     Context Orchestrator   │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │    LAYER 2: LAYA SYSTEM-1 DECISION      │
              │  • Source Selection Gate (Gmail: 94%)   │
              │  • Tool Query Generation                │
              │  • Stop condition & budget control      │
              └────────────────────┬────────────────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │    LAYER 3: COMPOSIO CONNECTORS         │
              │  Gmail │ Calendar │ Drive │ GitHub      │
              │  Managed OAuth + Hosted MCP Session     │
              └────────────────────┬────────────────────┘
                                   │ Raw Candidates
                                   ▼
              ┌─────────────────────────────────────────┐
              │    LAYER 4: SELECTION & PROVENANCE      │
              │  • Canonical ContextItem Normalization   │
              │  • BGE Reranker (200 → 13 → 9 items)    │
              │  • Conflict & Chronology Verification   │
              └────────────────────┬────────────────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │    LAYER 5: LAYA SUFFICIENCY GATE       │
              │  "Is evidence sufficient to generate?"  │
              │   YES (93%) ──────→ Grounded Generation │
              │   NO        ──────→ Targeted Query Loop │
              └────────────────────┬────────────────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │    GROUNDED GENERATION (OPEN-WEIGHT)    │
              │  Qwen3-8B conditioned strictly on the   │
              │  9 verified evidence citations          │
              └─────────────────────────────────────────┘
```

---

## 🔬 Core Innovation: System-1 Decisions (Laya 421M) vs. LLM

Conventional AI agents use a heavy LLM to reason about every single tool call, resulting in severe prompt bloat, high latency, and heavy VRAM usage:

```
Conventional Agent:
User ➔ LLM ➔ MCP ➔ 10 Tools ➔ 150 items dumped in prompt ➔ Slow Answer

Write4U Architecture:
User ➔ Task Parser ➔ Laya (System-1 Decision) ➔ Composio MCP ➔ Context Selection ➔ Laya Sufficiency Gate ➔ Grounded LLM
```

### Why Laya 421M?
1. **Lightweight & Fast**: At 421M parameters (Apache-2.0), Laya executes typed decisions in **~1.7 ms** with **<800 MB VRAM** footprint (fits effortlessly on an RTX 3050 4 GB).
2. **Specialized Typed Gates**:
   * **Source Gate**: Evaluates $P(\text{Source}_i \text{ is required} \mid \text{Task } T)$. Skips irrelevant personal sources (e.g. LinkedIn or personal files) before any API call is made.
   * **Sufficiency Gate**: Checks evidence coverage against required task entities, stopping retrieval early when evidence is sufficient.

---

## 📊 Empirical Benchmark Results

We evaluated 200 personal context signals across three distinct architectures:

| Metric | Baseline A: Vanilla LLM | Baseline B: Normal Agent | Write4U (Ours) | Advantage |
| :--- | :---: | :---: | :---: | :---: |
| **Tool Calling Pattern** | 0 calls | Unbounded (all tools) | **Gated by Laya** | **Selective execution** |
| **Context Sent** | 0 items | 200 items (100%) | **9 items (C\*)** | **95.5% reduction** |
| **Token Consumption** | 380 tokens | 4,194 tokens | **511 tokens** | **87.8% token savings** |
| **Irrelevant Noise** | 100% (No grounding) | 95.5% noise | **0.0% noise** | **Complete noise filter** |
| **Factual Grounding** | 35.0% (Hallucinated) | 68.0% (Distracted) | **98.0% verified** | **+30% accuracy** |
| **End-to-End Latency** | 320 ms | 4,320 ms | **460 ms** | **9.4× faster** |

*Run locally anytime via: `python evaluation/benchmark.py`*

---

## 🔌 Composio Unified Connector Layer

Write4U uses **Composio** as pure infrastructure:
* **Managed OAuth**: User connects Gmail, Calendar, Drive without maintaining separate Google Cloud credentials.
* **Hosted MCP Sessions**: Exposes tools via `session.mcp.url` with read-only scopes.
* **Deterministic Fallback**: Includes an interconnected 200-signal mock dataset in [`backend/data/mock_data/`](backend/data/mock_data/) for offline testing and deterministic evaluation.

---

## 🚀 Quickstart Guide

### 1. Configure Environment
```bash
cp .env.example .env
# Optional: Set COMPOSIO_API_KEY in .env
```

### 2. Start the FastAPI Engine
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
View OpenAPI specs at `http://127.0.0.1:8000/docs`.

### 3. Load the Chrome Extension
1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the [`extension/`](extension/) directory.
4. Open **Gmail** or **LinkedIn** to use Write4U directly in your composer.

### 4. Or Try the Web Demo Simulator
Open [`web_demo/index.html`](web_demo/index.html) in your browser to inspect the Laya decision gates, candidate funnel, and simulated Gmail/LinkedIn composers.

### 5. Run the Automated Test Suite
```bash
pytest -v
```
All 12 unit and integration tests pass in ~0.30s.

---

## 📜 Open-Source License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
