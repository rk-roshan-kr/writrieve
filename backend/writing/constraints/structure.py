import re
from typing import List, Tuple

class StructureConstraints:
    """
    Verifies that the generated draft contains the structural elements specified by the blueprint.
    """

    @classmethod
    def evaluate(cls, text: str, medium: str, required_sequence: List[str]) -> Tuple[bool, List[str], List[str]]:
        satisfied = []
        missing = []
        text_lower = text.lower()

        if medium == "email":
            # Check greeting
            if any(g in text_lower for g in ["dear", "hi ", "hello"]):
                satisfied.append("greeting")
            else:
                missing.append("greeting")

            # Check context / thank you
            if any(w in text_lower for w in ["thank", "great to", "enjoyed", "following up", "discussion"]):
                satisfied.append("thank_you_or_context")
            else:
                missing.append("thank_you_or_context")

            # Check next step / call to action
            if any(w in text_lower for w in ["call", "meet", "discuss", "next steps", "let me know", "would you"]):
                satisfied.append("proposed_next_step")
            else:
                missing.append("proposed_next_step")

            # Check closing / signoff
            if any(c in text_lower for c in ["best,", "regards,", "warmly,", "sincerely"]):
                satisfied.append("closing_signoff")
            else:
                missing.append("closing_signoff")

        elif medium == "linkedin":
            # Check hook (first sentence punchy)
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            if paragraphs and len(paragraphs[0]) > 10:
                satisfied.append("declarative_hook")
            else:
                missing.append("declarative_hook")

            # Check hashtags
            hashtags = re.findall(r"#\w+", text)
            if len(hashtags) >= 2:
                satisfied.append("hashtags")
            else:
                missing.append("hashtags")

            # Check gratitude / collaborators
            if any(w in text_lower for w in ["thanks", "grateful", "shoutout", "collaborators", "team", "advisor"]):
                satisfied.append("collaborator_gratitude")
            else:
                missing.append("collaborator_gratitude")

        is_valid = len(missing) == 0
        return is_valid, satisfied, missing
