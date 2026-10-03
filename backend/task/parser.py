import re
from typing import Dict, Any, Optional, List
from .classifier import TaskRepresentation, TaskClass

class TaskParser:
    """
    Parses user natural language prompts and live browser context into a structured TaskRepresentation.
    Detects entities, ambiguities, tone, topics, and initial uncertainties.
    """

    @classmethod
    def parse(cls, prompt: str, page_context: Optional[Dict[str, Any]] = None) -> TaskRepresentation:
        page_ctx = page_context or {}
        site = page_ctx.get("site", "gmail")
        recipient = page_ctx.get("recipient", "")
        subject = page_ctx.get("subject", "")

        # Target entity extraction
        target_entity = None
        target_aliases: List[str] = []
        uncertainties: List[str] = []

        if recipient:
            # e.g., "Prof. Xavier Vance <xvance@csail.mit.edu>"
            match = re.search(r"([^<]+)", recipient)
            if match:
                clean_name = match.group(1).strip()
                target_entity = clean_name
                # Derive aliases
                if "Prof." in clean_name or "Professor" in clean_name:
                    parts = clean_name.replace("Prof.", "").replace("Professor", "").strip().split()
                    if parts:
                        target_aliases.extend([parts[-1], f"Prof. {parts[-1]}", f"Professor {parts[-1]}"])
                target_aliases.append(clean_name)
        else:
            # Extract from prompt (e.g. "Prof. Xavier Vance" or "the professor I met at the conference")
            title_match = re.search(r"(?:prof\.|professor|dr\.)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)", prompt, re.IGNORECASE)
            if title_match:
                full_name = title_match.group(0).strip()
                target_entity = full_name
                target_aliases.extend([title_match.group(1).strip(), full_name])
            elif "professor" in prompt.lower() or "prof" in prompt.lower():
                target_entity = "Professor"
                uncertainties.append("Exact professor identity unknown from prompt alone")
            elif "rahul" in prompt.lower():
                target_entity = "Rahul"
                uncertainties.append("Multiple people named Rahul ممکن exist in contacts")

        # Event context
        event_context = None
        if "conference" in prompt.lower() or "ccncps" in prompt.lower():
            event_context = "CCNCPS Conference"
        elif "hackathon" in prompt.lower():
            event_context = "Hackathon"

        # Topic
        topic = None
        if "fieldchain" in prompt.lower() or "adaptive sharding" in prompt.lower():
            topic = "FieldChain & Adaptive Sharding"
        elif "project" in prompt.lower():
            topic = "Project Continuation"

        # Tone
        tone = "professional"
        if "casual" in prompt.lower() or "friendly" in prompt.lower() or "don't sound too formal" in prompt.lower():
            tone = "approachable_professional"

        # Classify task
        task_class = TaskClass.CLASS_C_GENERATION
        if uncertainties and ("which" in prompt.lower() or not recipient):
            task_class = TaskClass.CLASS_D_AMBIGUOUS if "rahul" in prompt.lower() else TaskClass.CLASS_C_GENERATION
        elif "what time" in prompt.lower() or "when is" in prompt.lower():
            task_class = TaskClass.CLASS_A_LOOKUP
        elif "summarize" in prompt.lower() or "summary" in prompt.lower():
            task_class = TaskClass.CLASS_B_SYNTHESIS
        elif "salary" in prompt.lower() or "financial" in prompt.lower() or "bank" in prompt.lower():
            task_class = TaskClass.CLASS_E_SENSITIVE

        # Freshness preference
        freshness = "balanced"
        if task_class == TaskClass.CLASS_A_LOOKUP:
            freshness = "strict_recent"
        elif "how did i meet" in prompt.lower() or "history" in prompt.lower():
            freshness = "historical_ok"

        constraints = ["do_not_hallucinate", "rely_strictly_on_verified_evidence"]
        if "don't sound too formal" in prompt.lower():
            constraints.append("avoid_excessive_formality")

        return TaskRepresentation(
            user_prompt=prompt,
            site=site,
            task_class=task_class,
            target_entity=target_entity,
            target_aliases=list(set(target_aliases)),
            event_context=event_context,
            topic=topic,
            desired_tone=tone,
            constraints=constraints,
            uncertainties=uncertainties,
            risk_level="low",
            freshness_preference=freshness
        )
