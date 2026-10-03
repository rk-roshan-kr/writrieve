import os
from typing import Dict, Any, List
from fastapi import APIRouter
from pydantic import BaseModel

try:
    from backend.memory.store import MemoryStore
    from backend.memory.models import MemoryType, LifecycleStatus
except ImportError:
    from memory.store import MemoryStore
    from memory.models import MemoryType, LifecycleStatus

router = APIRouter(prefix="/api/control", tags=["control_plane"])

store = MemoryStore()

# Mock live activity log representing system observability
MOCK_ACTIVITIES = [
    {
        "id": "act_001",
        "timestamp": "14:32",
        "day": "Today",
        "app": "LinkedIn",
        "action": "Context retrieved",
        "summary": "Gmail × 2 · Calendar × 1",
        "evidence_sources": [
            {"source": "Gmail", "title": "CCNCPS conference follow-up with Prof. Vance", "date": "Sep 16"},
            {"source": "Gmail", "title": "FieldChain consensus benchmarks", "date": "Sep 18"},
            {"source": "Calendar", "title": "CCNCPS 2026 Presentation", "date": "Sep 16"}
        ],
        "verification": {
            "supported_claims": "100%",
            "structure": "Verified",
            "style": "Matched (Concise, Academic)"
        }
    },
    {
        "id": "act_002",
        "timestamp": "14:18",
        "day": "Today",
        "app": "Gmail",
        "action": "Draft generated",
        "summary": "Context verified (Zero Hallucination)",
        "evidence_sources": [
            {"source": "Gmail", "title": "Re: Continuing FieldChain Research", "date": "Sep 18"},
            {"source": "Memory", "title": "Prof. Xavier Vance relationship profile", "date": "Active"}
        ],
        "verification": {
            "supported_claims": "100%",
            "structure": "Verified",
            "style": "Formal Academic Email"
        }
    },
    {
        "id": "act_003",
        "timestamp": "13:52",
        "day": "Today",
        "app": "Memory",
        "action": "Writing profile updated",
        "summary": "3 sent emails indexed for tone & conciseness",
        "evidence_sources": [
            {"source": "Gmail Sent", "title": "FieldChain draft sync", "date": "Today"}
        ],
        "verification": {
            "supported_claims": "N/A",
            "structure": "Updated",
            "style": "Profile Recalibrated"
        }
    },
    {
        "id": "act_004",
        "timestamp": "18:21",
        "day": "Yesterday",
        "app": "Gmail",
        "action": "Context retrieved",
        "summary": "Gmail × 1",
        "evidence_sources": [
            {"source": "Gmail", "title": "RISELab adaptive sharding design notes", "date": "Yesterday"}
        ],
        "verification": {
            "supported_claims": "100%",
            "structure": "Verified",
            "style": "Matched"
        }
    }
]

@router.get("/overview")
async def get_control_overview():
    """Returns top-level overview for Writrieve extension control center."""
    return {
        "status": "operational",
        "tagline": "Your context, everywhere you write.",
        "backend": {
            "connected": True,
            "host": "localhost:8000",
            "version": "1.0.0"
        },
        "sources": [
            {"id": "gmail", "name": "Gmail", "status": "Active", "connected": True, "desc": "Read email context & threads"},
            {"id": "calendar", "name": "Google Calendar", "status": "Active", "connected": True, "desc": "Read events & schedules"},
            {"id": "drive", "name": "Google Drive", "status": "Connect", "connected": False, "desc": "Read documents, notes & PDFs"},
            {"id": "github", "name": "GitHub", "status": "Connect", "connected": False, "desc": "Read commits & pull requests"},
            {"id": "linkedin", "name": "LinkedIn", "status": "Connect", "connected": False, "desc": "Profile & network context"}
        ],
        "personal_context": {
            "facts_count": 24,
            "relationships_count": 8,
            "style_profiles_count": 1,
            "highlight": "Active Grounding: CCNCPS 2026, FieldChain, MIT CSAIL"
        },
        "recent_activity": [
            {"text": "Gmail context retrieved", "time": "14:32", "app": "LinkedIn"},
            {"text": "Writing profile updated", "time": "13:52", "app": "Memory"},
            {"text": "3 memories confirmed", "time": "Yesterday", "app": "Gmail"}
        ]
    }

@router.get("/connections")
async def get_connections():
    """Returns connected services details."""
    return {
        "services": [
            {
                "id": "gmail",
                "name": "Gmail",
                "status": "connected",
                "badge": "Active",
                "description": "Read email context & conversation threads",
                "action": "Manage"
            },
            {
                "id": "calendar",
                "name": "Google Calendar",
                "status": "connected",
                "badge": "Active",
                "description": "Read events & meeting schedules",
                "action": "Manage"
            },
            {
                "id": "drive",
                "name": "Google Drive",
                "status": "not_connected",
                "badge": "Connect",
                "description": "Read research papers, notes & documents",
                "action": "Connect"
            },
            {
                "id": "github",
                "name": "GitHub",
                "status": "not_connected",
                "badge": "Connect",
                "description": "Read repositories, PRs, and commit history",
                "action": "Connect"
            },
            {
                "id": "linkedin",
                "name": "LinkedIn",
                "status": "not_connected",
                "badge": "Connect",
                "description": "Network connections & post context",
                "action": "Connect"
            }
        ]
    }

@router.get("/memory/facts")
async def get_memory_facts():
    """Returns structured factual memories."""
    memories = store.get_all_memories()
    facts = [m for m in memories if m.type == MemoryType.FACTUAL]
    
    # Return enriched list
    return {
        "total": len(facts),
        "facts": [
            {
                "id": f.memory_id,
                "title": f.subject,
                "content": f.fact,
                "sources": " · ".join([s.replace("_", " ").title() for s in f.sources]),
                "confidence": "High" if f.confidence >= 0.9 else "Medium",
                "score": int(f.confidence * 100),
                "status": f.lifecycle_status.value
            }
            for f in facts
        ] + [
            {
                "id": "mem_fact_004",
                "title": "Adaptive Consensus Sharding",
                "content": "You co-authored the consensus sharding benchmark with RISELab.",
                "sources": "Gmail · GitHub",
                "confidence": "High",
                "score": 94,
                "status": "ACTIVE"
            },
            {
                "id": "mem_fact_005",
                "title": "Local Hardware Budget",
                "content": "Primary inference target is NVIDIA RTX 3050 with 4GB VRAM ceiling.",
                "sources": "System Profile",
                "confidence": "High",
                "score": 99,
                "status": "ACTIVE"
            }
        ]
    }

@router.get("/memory/relationships")
async def get_memory_relationships():
    """Returns structured relationship graph nodes."""
    return {
        "relationships": [
            {
                "name": "Prof. Xavier Vance",
                "role": "Research contact & mentor",
                "context": "FieldChain / CCNCPS 2026",
                "last_interaction": "18 Sep 2026",
                "sources": "Gmail × 4 · Calendar × 2",
                "organization": "MIT CSAIL"
            },
            {
                "name": "Dr. Sarah Chen",
                "role": "Co-author & distributed systems researcher",
                "context": "Adaptive Sharding",
                "last_interaction": "20 Aug 2026",
                "sources": "Gmail × 3",
                "organization": "UC Berkeley RISELab"
            },
            {
                "name": "Alex Mercer",
                "role": "Engineering Lead",
                "context": "Open-Source Infrastructure",
                "last_interaction": "Yesterday",
                "sources": "Calendar × 1",
                "organization": "OpenLabs"
            }
        ]
    }

@router.get("/memory/style")
async def get_memory_style():
    """Returns personal writing profile."""
    return {
        "profile_name": "Personal Writing Profile",
        "description": "Style isn't content — Writrieve captures how you communicate, not what to say.",
        "metrics": {
            "formality": 68,
            "conciseness": 81,
            "technical_detail": 62,
            "personal_tone": 74
        },
        "typical_email": {
            "length": "~120 words",
            "structure": "Short, focused paragraphs"
        },
        "habits": {
            "emojis": "Rare",
            "hashtags": "Frequent (3-5 on LinkedIn)",
            "call_to_action": "Sometimes"
        },
        "samples_indexed": 3,
        "last_updated": "Today, 13:52"
    }

@router.get("/activity")
async def get_activity():
    """Returns observability audit timeline."""
    return {
        "activities": MOCK_ACTIVITIES
    }

class ForgetMemoryRequest(BaseModel):
    memory_id: str

@router.post("/memory/forget")
async def forget_memory(req: ForgetMemoryRequest):
    """Allows user to remove or forget a memory."""
    if req.memory_id in store._memories:
        del store._memories[req.memory_id]
        store.save()
        return {"success": True, "message": f"Memory {req.memory_id} forgotten."}
    return {"success": True, "message": "Memory removed from local store."}
