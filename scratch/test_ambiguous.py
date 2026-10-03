import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.orchestration.controller import Write4UContextController

controller = Write4UContextController()
result = controller.execute_task(
    user_prompt="Write an email to Rahul about the sync.",
    page_context={"site": "gmail"}
)

print("=== AMBIGUOUS ENTITY TEST ===")
print("Terminal Status:", result.terminal_status)
print("Clarification Prompt:", result.user_clarification)
print("Draft:", result.generated_draft)
