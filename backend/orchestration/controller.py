import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from backend.task.parser import TaskParser
from backend.task.requirements import RequirementsPlanner, InformationRequirement
from backend.task.classifier import TaskRepresentation, TaskClass
from backend.policy.budgets import RetrievalBudget
from backend.policy.permissions import PolicyPermissions
from backend.policy.risk import RiskEvaluator
from backend.retrieval.candidate import CandidateDiscoveryBroker
from backend.retrieval.entity_resolution import EntityResolver
from backend.retrieval.reranker import EvidenceSelectionEngine
from backend.evidence.state import EvidenceState, TerminalStatus
from backend.evidence.conflicts import ConflictDetector
from backend.evidence.confidence import ConfidenceEstimator
from backend.evidence.provenance import ProvenanceTracker
from backend.decision.laya import LayaSystem1Controller
from backend.decision.interface import DecisionAction, DecisionActionType
from backend.orchestration.stopping import StoppingController
from backend.orchestration.state_machine import StateMachine
from backend.generation.writer import ContextGroundedWriter
from backend.writing.engine import WritingTaskEngine, WritingResult
from backend.writing.blueprints.blueprint_schema import WritingBlueprint
from backend.writing.verification.pipeline import MultiPassVerificationReport
from backend.memory.store import MemoryStore
from backend.memory.retriever import MemoryRetriever
from backend.memory.extractor import MemoryExtractor
from backend.retrieval.web_broker import WebSearchBroker
from backend.orchestration.source_router import SourceRouter, SourcePlan
from backend.writing.evidence_packet import WritingEvidencePacket

try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

class IterationLog(BaseModel):
    iteration: int
    action: str
    source: Optional[str]
    query: Optional[str]
    candidates_count: int
    selected_evidence_count: int
    confidence_summary: Dict[str, float]
    reason: str

class Write4UControllerResult(BaseModel):
    task: TaskRepresentation
    evidence_state: EvidenceState
    selected_items: List[ContextItem]
    generated_draft: str
    claims_verification: List[Dict[str, Any]]
    iteration_history: List[IterationLog]
    budget_summary: Dict[str, Any]
    terminal_status: TerminalStatus
    user_clarification: Optional[str] = None
    writing_blueprint: Optional[WritingBlueprint] = None
    verification_report: Optional[MultiPassVerificationReport] = None
    retrieved_memories_count: int = 0
    new_memories_extracted_count: int = 0

class Write4UContextController:
    """
    Core Controller of Write4U v2.
    Implements the fault-tolerant, controlled iterative context acquisition loop.
    Coordinates Task Representation, Policy/Budget Engine, System-1 Decision Model,
    Retrieval Broker, Evidence State Processor, Sufficiency Gate, and Output Verifier.
    """

    def __init__(self, user_id: str = "write4u_default_user"):
        self.user_id = user_id
        self.broker = CandidateDiscoveryBroker(user_id=user_id)
        self.decision_model = LayaSystem1Controller()
        self.selection_engine = EvidenceSelectionEngine()
        self.writer = ContextGroundedWriter()
        self.writing_engine = WritingTaskEngine()
        self.memory_store = MemoryStore()
        self.memory_retriever = MemoryRetriever(self.memory_store)
        self.web_broker = WebSearchBroker()

    def execute_task(
        self,
        user_prompt: str,
        page_context: Optional[Dict[str, Any]] = None,
        budget_override: Optional[Dict[str, Any]] = None
    ) -> Write4UControllerResult:
        start_time = time.time()

        # Step 1 — Task Representation
        task = TaskParser.parse(prompt=user_prompt, page_context=page_context)

        # Step 2 — Policy & Budget Initialization
        risk_level, risk_desc = RiskEvaluator.evaluate(task)
        task.risk_level = risk_level

        budget = RetrievalBudget(**(budget_override or {}))
        requirements = RequirementsPlanner.derive_requirements(task)

        # Entity resolution on target
        resolved_entity = EntityResolver.resolve(task.target_entity or "")

        # Step 3 — Initialize Evidence State
        evidence_state = EvidenceState(
            task_id=f"task_{int(start_time)}",
            unknowns=list(task.uncertainties),
            terminal_status=TerminalStatus.ACQUIRING
        )

        # If entity resolution is ambiguous for an intended recipient, pause for clarification
        if task.target_entity and resolved_entity.is_ambiguous:
            evidence_state.terminal_status = TerminalStatus.ASK_USER
            evidence_state.clarification_prompt = (
                f"Multiple identities match '{task.target_entity}': "
                f"{', '.join(resolved_entity.competing_candidates)}. Please select the intended recipient."
            )
            return Write4UControllerResult(
                task=task,
                evidence_state=evidence_state,
                selected_items=[],
                generated_draft="[Execution paused: user clarification required for ambiguous entity]",
                claims_verification=[],
                iteration_history=[],
                budget_summary=budget.budget_summary(),
                terminal_status=TerminalStatus.ASK_USER,
                user_clarification=evidence_state.clarification_prompt
            )

        accumulated_candidates: List[ContextItem] = []
        iteration_history: List[IterationLog] = []

        # Step 3b — Long-term Memory Retrieval (Query memory before live sources)
        memory_bundle = self.memory_retriever.retrieve_for_task(task)
        retrieved_mem_count = len(memory_bundle["context_items"])
        if retrieved_mem_count > 0:
            accumulated_candidates.extend(memory_bundle["context_items"])
            evidence_state.items = list(memory_bundle["context_items"])
            evidence_state.sources_used.append("personal_memory")
            conf_scores = ConfidenceEstimator.evaluate(evidence_state, requirements)
            evidence_state.confidence_scores = conf_scores

        # Step 3c — External Web Search (Establish official background context)
        source_plan = SourceRouter.plan_sources(task)
        if "web" in source_plan.external_sources:
            web_query = task.event_context or f"{task.user_prompt} conference"
            web_candidates = self.web_broker.search_web(web_query)
            if web_candidates:
                accumulated_candidates.extend(web_candidates)
                evidence_state.sources_used.append("web")

        # Step 4 — The Controlled Iterative Acquisition Loop
        while not budget.is_exhausted() and evidence_state.terminal_status == TerminalStatus.ACQUIRING:
            evidence_state.iteration += 1

            # Decision Model decides next action
            action: DecisionAction = self.decision_model.decide(
                task=task,
                state=evidence_state,
                budget=budget,
                requirements=requirements
            )

            # Handle Terminal Decision Actions
            if action.action == DecisionActionType.STOP:
                evidence_state.terminal_status = TerminalStatus.SUCCESS
                iteration_history.append(IterationLog(
                    iteration=evidence_state.iteration,
                    action=action.action.value,
                    source=None,
                    query=None,
                    candidates_count=0,
                    selected_evidence_count=len(evidence_state.items),
                    confidence_summary=dict(evidence_state.confidence_scores),
                    reason=action.reason
                ))
                break

            elif action.action == DecisionActionType.ABSTAIN:
                evidence_state.terminal_status = TerminalStatus.ABSTAIN
                iteration_history.append(IterationLog(
                    iteration=evidence_state.iteration,
                    action=action.action.value,
                    source=None,
                    query=None,
                    candidates_count=0,
                    selected_evidence_count=len(evidence_state.items),
                    confidence_summary=dict(evidence_state.confidence_scores),
                    reason=action.reason
                ))
                break

            elif action.action == DecisionActionType.ASK_USER:
                evidence_state.terminal_status = TerminalStatus.ASK_USER
                evidence_state.clarification_prompt = action.reason
                break

            # Handle Retrieval Actions (QUERY_SOURCE, REFINE_QUERY, VERIFY_CONFLICT)
            source_to_query = action.source or "gmail"
            query_str = action.query or task.user_prompt

            new_candidates = self.broker.discover_candidates(
                source=source_to_query,
                query=query_str,
                budget=budget,
                limit=35
            )

            accumulated_candidates.extend(new_candidates)
            if source_to_query not in evidence_state.sources_used:
                evidence_state.sources_used.append(source_to_query)

            # Evidence Processing: Stage B Reranking & Selection
            scored_evidence = self.selection_engine.select_evidence(
                candidates=accumulated_candidates,
                task=task,
                resolved_entity=resolved_entity,
                max_evidence=9
            )
            evidence_state.items = [s.item for s in scored_evidence]

            # Conflict Detection
            conflicts = ConflictDetector.scan_for_conflicts(evidence_state.items)
            evidence_state.conflicts = conflicts

            # Confidence Update across requirements
            conf_scores = ConfidenceEstimator.evaluate(evidence_state, requirements)
            evidence_state.confidence_scores = conf_scores

            # Record iteration log
            iteration_history.append(IterationLog(
                iteration=evidence_state.iteration,
                action=action.action.value,
                source=source_to_query,
                query=query_str,
                candidates_count=len(new_candidates),
                selected_evidence_count=len(evidence_state.items),
                confidence_summary=dict(conf_scores),
                reason=action.reason
            ))

            # Evaluate Stopping Conditions
            should_stop, status, reason = StoppingController.evaluate(
                state=evidence_state,
                budget=budget,
                requirements=requirements
            )
            if should_stop:
                evidence_state.terminal_status = status
                break

        # If still in ACQUIRING after loop, determine final terminal status
        if evidence_state.terminal_status == TerminalStatus.ACQUIRING:
            evidence_state.terminal_status = (
                TerminalStatus.PARTIAL if evidence_state.items else TerminalStatus.ABSTAIN
            )

        # Step 5 — Generation & Multi-Pass Output Verification
        draft_text = ""
        claims_verifications = []
        writing_bp = None
        verif_rep = None

        if evidence_state.terminal_status in {TerminalStatus.SUCCESS, TerminalStatus.PARTIAL}:
            writing_result = self.writing_engine.execute_writing(
                task=task,
                evidence=evidence_state
            )
            draft_text = writing_result.final_draft
            writing_bp = writing_result.blueprint
            verif_rep = writing_result.verification

            # Closed-Loop Feedback: If unsupported claims exist, attempt targeted re-retrieval
            if verif_rep.factual_report.has_unsupported_claims and not budget.is_exhausted():
                unsupported_claims = [c for c in verif_rep.factual_report.claims if c.status == "UNSUPPORTED"]
                recovered_count = 0
                for unsupp in unsupported_claims:
                    clean_words = [w for w in unsupp.claim_text.split() if len(w) > 4 and w.isalnum()]
                    if clean_words:
                        targeted_q = " ".join(clean_words[:4])
                        recovered_candidates = self.broker.discover_candidates("gmail", targeted_q, budget)
                        if recovered_candidates:
                            evidence_state.items.extend(recovered_candidates)
                            recovered_count += 1
                if recovered_count > 0:
                    # Re-verify and update draft with newly verified context
                    re_result = self.writing_engine.execute_writing(task=task, evidence=evidence_state)
                    draft_text = re_result.final_draft
                    verif_rep = re_result.verification

            claims_verifications = [c.model_dump() for c in verif_rep.factual_report.claims]
        elif evidence_state.terminal_status == TerminalStatus.ABSTAIN:
            draft_text = "I do not have sufficient verified evidence from your personal context to reliably draft this message without risking hallucination."
        elif evidence_state.terminal_status == TerminalStatus.ASK_USER:
            draft_text = f"Clarification requested: {evidence_state.clarification_prompt}"

        # Step 6 — Progressive Memory Extraction ("Memory Update?")
        new_memories = MemoryExtractor.extract_from_evidence(
            evidence_items=evidence_state.items,
            store=self.memory_store
        )

        return Write4UControllerResult(
            task=task,
            evidence_state=evidence_state,
            selected_items=evidence_state.items,
            generated_draft=draft_text,
            claims_verification=claims_verifications,
            iteration_history=iteration_history,
            budget_summary=budget.budget_summary(),
            terminal_status=evidence_state.terminal_status,
            user_clarification=evidence_state.clarification_prompt,
            writing_blueprint=writing_bp,
            verification_report=verif_rep,
            retrieved_memories_count=retrieved_mem_count,
            new_memories_extracted_count=len(new_memories)
        )
