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

        # If entity resolution is ambiguous, immediately transition to ASK_USER
        if resolved_entity.is_ambiguous:
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

        # Step 5 — Generation & Output Verification
        draft_text = ""
        claims_verifications = []

        if evidence_state.terminal_status in {TerminalStatus.SUCCESS, TerminalStatus.PARTIAL}:
            draft_text, claims = self.writer.write_and_verify(
                user_prompt=user_prompt,
                evidence_items=evidence_state.items,
                tone=task.desired_tone
            )
            claims_verifications = [c.dict() for c in claims]
        elif evidence_state.terminal_status == TerminalStatus.ABSTAIN:
            draft_text = "I do not have sufficient verified evidence from your personal context to reliably draft this message without risking hallucination."
        elif evidence_state.terminal_status == TerminalStatus.ASK_USER:
            draft_text = f"Clarification requested: {evidence_state.clarification_prompt}"

        return Write4UControllerResult(
            task=task,
            evidence_state=evidence_state,
            selected_items=evidence_state.items,
            generated_draft=draft_text,
            claims_verification=claims_verifications,
            iteration_history=iteration_history,
            budget_summary=budget.budget_summary(),
            terminal_status=evidence_state.terminal_status,
            user_clarification=evidence_state.clarification_prompt
        )
