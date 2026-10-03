import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.orchestration.controller import Write4UContextController

controller = Write4UContextController()
result = controller.execute_task(
    user_prompt="Write a follow-up to the professor I met at the conference. Mention our discussion about continuing the project, but don't sound too formal.",
    page_context={"site": "gmail"}
)

print("=== STATUS ===")
print("Terminal Status:", result.terminal_status)
print("Task Class:", result.task.task_class)
print("Target Entity:", result.task.target_entity)
print("Topic:", result.task.topic)
print("Tone:", result.task.desired_tone)
print("\n=== ITERATIONS ===")
for it in result.iteration_history:
    print(f"Iter {it.iteration}: Action={it.action} Source={it.source} Query='{it.query}' Candidates={it.candidates_count} Selected={it.selected_evidence_count} Conf={it.confidence_summary}")
print("\n=== BUDGET ===")
print(result.budget_summary)
print("\n=== DRAFT ===")
print(result.generated_draft)
print("\n=== CLAIMS VERIFIED ===")
for c in result.claims_verification:
    print(f"[{c['status']}] {c['claim_text']} (evidence: {c['supporting_evidence_ids']})")
