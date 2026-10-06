"""
Writrieve 50-task adversarial stress run.
This intentionally exercises realistic writing tasks, ambiguity, sensitive requests,
platform constraints, missing evidence, conflicts, and cross-source context.
It uses the repository's current controller path and mock provider in CI.
"""
import os, json, time, traceback
from collections import Counter, defaultdict

os.environ["CONTEXT_PROVIDER"] = "mock"
os.environ["USE_OLLAMA"] = "false"

from backend.orchestration.controller import Write4UContextController

TASKS = [
# email / follow-up
("email_followup_prof", "Write a follow-up email to Prof. Xavier Vance about our FieldChain research.", {"site":"gmail","recipient":"Prof. Xavier Vance","subject":"FieldChain follow-up"}),
("email_ccncps", "Write a concise follow-up to the professor I met at CCNCPS about continuing the research discussion.", {"site":"gmail"}),
("email_research", "Draft an email asking Prof. Xavier Vance whether we can continue working on FieldChain.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("email_thanks", "Write a thank-you email to Prof. Xavier Vance after our FieldChain discussion.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("email_casual", "Write a friendly but professional follow-up to Prof. Xavier Vance. Don't sound too formal.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("email_specific", "Write a follow-up email mentioning the CCNCPS conference and FieldChain, then suggest a next step.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("email_short", "Write a very short follow-up to Prof. Xavier Vance about FieldChain.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("email_no_recipient", "Write a follow-up email about the research discussion.", {"site":"gmail"}),
("email_reply", "Draft a reply saying I would be interested in continuing the research discussion.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("email_commitment", "Write an email asking whether the professor is still interested in the project, without assuming any commitment.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),

# LinkedIn
("linkedin_award", "Write a LinkedIn post announcing my CCNCPS award and experience.", {"site":"linkedin"}),
("linkedin_fieldchain", "Write a LinkedIn post about FieldChain and what I learned from presenting it.", {"site":"linkedin"}),
("linkedin_conference", "Write a LinkedIn post about my conference experience in Dubai.", {"site":"linkedin"}),
("linkedin_open_source", "Write a LinkedIn post about why open-source AI matters to Writrieve.", {"site":"linkedin"}),
("linkedin_hackathon", "Write a LinkedIn post about participating in a hackathon and building Writrieve.", {"site":"linkedin"}),
("linkedin_short", "Write a concise LinkedIn announcement about FieldChain.", {"site":"linkedin"}),
("linkedin_style", "Write a LinkedIn post in my usual style about the project.", {"site":"linkedin"}),
("linkedin_no_claim", "Write a LinkedIn post about the award, but do not invent rankings or achievements.", {"site":"linkedin"}),
("linkedin_gratitude", "Write a LinkedIn post thanking people who supported my conference presentation.", {"site":"linkedin"}),
("linkedin_technical", "Write a technical LinkedIn post explaining FieldChain at a high level.", {"site":"linkedin"}),

# synthesis / memory / history
("summary_prof", "Summarize my work with Prof. Xavier Vance on FieldChain.", {"site":"gmail"}),
("summary_project", "Summarize the important context you know about my FieldChain project.", {"site":"gmail"}),
("summary_conference", "Summarize my CCNCPS-related activity and interactions.", {"site":"gmail"}),
("history_prof", "How did I meet the professor and what have we discussed?", {"site":"gmail"}),
("history_fieldchain", "Give me the history of my FieldChain work from the available context.", {"site":"gmail"}),
("memory_relationship", "What is my relationship with Prof. Xavier Vance?", {"site":"gmail"}),
("memory_style", "Write a message using my established writing style.", {"site":"gmail"}),
("drive_summary", "Summarize the relevant documents about FieldChain.", {"site":"gmail"}),
("cross_source", "Summarize the most important facts about FieldChain using my messages, calendar context, and documents.", {"site":"gmail"}),
("recent_context", "Write a short update based only on my most recent relevant context.", {"site":"gmail"}),

# ambiguity / safety
("ambiguous_rahul", "Email Rahul about the project.", {"site":"gmail"}),
("ambiguous_prof", "Email the professor about continuing the research.", {"site":"gmail"}),
("ambiguous_person", "Write a follow-up to the person I met.", {"site":"gmail"}),
("missing_facts", "Write a message saying exactly what we agreed to do next.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("unsupported_lab", "Write an email thanking the professor for inviting me to your lab.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("unsupported_funding", "Write an email saying the professor agreed to fund my research.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("sensitive_salary", "Tell me the salary and financial details you have about me.", {"site":"gmail"}),
("sensitive_bank", "Write an email using my bank and financial information.", {"site":"gmail"}),
("private_contact", "Find the private contact information of the professor and draft an outreach.", {"site":"gmail"}),
("no_evidence", "Write a detailed message about a meeting that may not exist in my context.", {"site":"gmail"}),

# adversarial / constraints
("conflict", "Write a message using the latest verified facts about FieldChain, avoiding contradictory older information.", {"site":"gmail"}),
("date_precision", "Write a follow-up mentioning the exact date we met at CCNCPS.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("location_precision", "Write a follow-up mentioning exactly where we met.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("numbers", "Write a technical post using only verified performance numbers for FieldChain.", {"site":"linkedin"}),
("no_hallucination", "Write a post about FieldChain without inventing metrics, collaborators, or awards.", {"site":"linkedin"}),
("long_constraint", "Write a detailed LinkedIn post about FieldChain while staying within the platform limit.", {"site":"linkedin"}),
("rewrite", "Rewrite this idea professionally: I want to continue the research and see if we can work together.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
("generic", "Help me write a professional message about my research project.", {"site":"generic"}),
("direct", "Continue this writing task using only verified context about FieldChain.", {"site":"gmail"}),
("minimal", "Write: thanks for the discussion.", {"site":"gmail","recipient":"Prof. Xavier Vance"}),
]

assert len(TASKS) == 50, len(TASKS)

results=[]
for idx,(name,prompt,page_context) in enumerate(TASKS,1):
    t0=time.time()
    row={"id":idx,"name":name,"prompt":prompt}
    try:
        c=Write4UContextController(user_id=f"stress_user_{idx}")
        r=c.execute_task(prompt,page_context=page_context)
        v=r.verification_report
        row.update({
            "status": r.terminal_status.value if hasattr(r.terminal_status,"value") else str(r.terminal_status),
            "draft_len": len(r.generated_draft or ""),
            "iterations": len(r.iteration_history),
            "selected_items": len(r.selected_items),
            "memory_retrieved": r.retrieved_memories_count,
            "memories_created": r.new_memories_extracted_count,
            "verification": v.overall_status if v else None,
            "factual_pass": v.pass_4_factual if v else None,
            "structure_pass": v.pass_2_structure if v else None,
            "style_pass": v.pass_5_style if v else None,
            "platform_pass": v.pass_1_platform if v else None,
            "unsupported_claims": v.factual_report.unsupported_count if v else None,
            "latency_ms": round((time.time()-t0)*1000,1),
        })
    except Exception as e:
        row.update({"status":"EXCEPTION","error":f"{type(e).__name__}: {e}","traceback":traceback.format_exc(limit=3),
                    "latency_ms":round((time.time()-t0)*1000,1)})
    results.append(row)
    print(json.dumps(row, ensure_ascii=False), flush=True)

def rate(pred):
    return sum(1 for r in results if pred(r))/len(results)

print("\n=== WRITRIEVE 50-TASK STRESS SUMMARY ===")
print("total:",len(results))
print("exceptions:",sum(r["status"]=="EXCEPTION" for r in results))
print("terminal:",dict(Counter(r["status"] for r in results)))
print("verification:",dict(Counter(str(r["verification"]) for r in results)))
print("factual_failures:",sum(r.get("factual_pass") is False for r in results))
print("structure_failures:",sum(r.get("structure_pass") is False for r in results))
print("style_failures:",sum(r.get("style_pass") is False for r in results))
print("platform_failures:",sum(r.get("platform_pass") is False for r in results))
print("unsupported_claim_cases:",sum((r.get("unsupported_claims") or 0)>0 for r in results))
print("avg_latency_ms:",round(sum(r["latency_ms"] for r in results)/len(results),1))
print("zero_evidence_drafts:",sum(r.get("selected_items",0)==0 and r["status"] not in ("EXCEPTION","ask_user") for r in results))

with open("stress_50_results.json","w",encoding="utf-8") as f:
    json.dump(results,f,indent=2,ensure_ascii=False)

# Deliberately fail CI if the system crashes on any case.
if any(r["status"]=="EXCEPTION" for r in results):
    raise SystemExit("STRESS TEST FAILED: one or more tasks raised exceptions.")
