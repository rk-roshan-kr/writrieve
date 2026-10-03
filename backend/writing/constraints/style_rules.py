import re
from typing import Dict, Any, Tuple
from backend.writing.profiles.style_profile import PersonalWritingProfile

class StyleConstraints:
    """
    Compares the generated text with the user's personal writing profile to detect style drift.
    """

    @classmethod
    def evaluate(cls, text: str, profile: PersonalWritingProfile) -> Tuple[bool, Dict[str, Any], str]:
        diagnostics = {}
        issues = []

        if profile.active_medium == "email":
            # Sentence length
            sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
            avg_words = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            diagnostics["avg_sentence_words"] = round(avg_words, 1)

            target_words = profile.email.avg_sentence_length_words or 16
            if abs(avg_words - target_words) > 10:
                issues.append(f"Sentence rhythm deviates from user norm (got {avg_words:.1f}, user typical: {target_words})")

        elif profile.active_medium == "linkedin":
            hashtags = re.findall(r"#\w+", text)
            diagnostics["hashtag_count"] = len(hashtags)
            expected_tags = profile.linkedin.typical_hashtag_count or 4

            if len(hashtags) > expected_tags + 3:
                issues.append("Excessive hashtags compared to user profile.")

        is_aligned = len(issues) == 0
        summary = "Style is well aligned with user profile." if is_aligned else "; ".join(issues)
        return is_aligned, diagnostics, summary
