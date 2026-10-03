from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ContextItem(BaseModel):
    id: str
    source: str  # gmail, calendar, linkedin, drive, github, contacts
    type: str    # email, event, post, doc, commit, contact
    timestamp: str # ISO or YYYY-MM-DD
    people: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    content: str
    reliability: float = 0.9
    permissions: List[str] = Field(default_factory=lambda: ["personal"])
    provenance: Dict[str, Any] = Field(default_factory=dict)

class TaskIntent(BaseModel):
    raw_prompt: str
    task_type: str  # email_followup, linkedin_post, paper_summary, recommendation_request, etc.
    primary_entity: Optional[str] = None
    recipient: Optional[str] = None
    intent_description: str
    tone: Optional[str] = "professional"

class ContextPlan(BaseModel):
    task_type: str
    entities: List[str]
    requirements: List[str]
    preferred_sources: List[str]
    time_window: Optional[str] = "last_6_months"
    min_evidence_needed: int = 5
    max_evidence_needed: int = 10

class ScoreBreakdown(BaseModel):
    semantic_relevance: float
    entity_relevance: float
    temporal_relevance: float
    source_reliability: float
    task_relevance: float
    redundancy_penalty: float
    privacy_penalty: float
    total_score: float
    rationale: List[str] = Field(default_factory=list)

class ScoredContextItem(BaseModel):
    item: ContextItem
    score_breakdown: ScoreBreakdown
    rank: int
    selected: bool = False

class ClaimEvidence(BaseModel):
    claim_id: str
    claim_text: str
    verified: bool
    evidence_ids: List[str]
    evidence_summaries: List[str]
    confidence: float

class GenerationRequest(BaseModel):
    prompt: str
    mode: Optional[str] = "write4u" # "write4u" | "rag" | "baseline"
    model_provider: Optional[str] = "open_weights" # "open_weights" (Qwen/Llama/Groq/Ollama) | "openai" | "gemini"
    api_key: Optional[str] = None
    endpoint_url: Optional[str] = None

class GenerationStepLog(BaseModel):
    step: str
    description: str
    details: Dict[str, Any]

class GenerationResponse(BaseModel):
    draft: str
    task_intent: TaskIntent
    context_plan: ContextPlan
    stats: Dict[str, Any]
    candidate_distribution: Dict[str, int]
    funnel: Dict[str, int] # e.g. {"candidates": 143, "ranked": 18, "selected": 7}
    selected_evidence: List[ScoredContextItem]
    claims_provenance: List[ClaimEvidence]
    selection_reasons: List[str]
    pipeline_logs: List[GenerationStepLog]

class BenchmarkMetric(BaseModel):
    system: str  # "Write4U (Context Planned)", "Standard RAG", "Naive Baseline (All Context)"
    tokens_used: int
    context_items_sent: int
    irrelevant_context_rate: float
    latency_ms: float
    factual_accuracy_score: float
    source_coverage_score: float
    explanation: str
