import re
from typing import List, Dict, Any
from .style_profile import PersonalWritingProfile, EmailStyleMetrics, LinkedInStyleMetrics

class StyleAnalyzer:
    """
    Extracts observable stylistic patterns from raw written texts (sent emails / LinkedIn posts).
    Strips semantic content to avoid leaking outdated facts while capturing rhythm, length,
    vocabulary, and formatting habits.
    """

    @classmethod
    def analyze_emails(cls, email_texts: List[str]) -> EmailStyleMetrics:
        if not email_texts:
            return EmailStyleMetrics()

        total_chars = sum(len(t) for t in email_texts)
        avg_len = total_chars // len(email_texts)

        # Sentence length
        all_sentences = []
        for t in email_texts:
            sents = [s for s in re.split(r"[.!?]+", t) if s.strip()]
            all_sentences.extend(sents)

        avg_sent_words = 16
        if all_sentences:
            word_counts = [len(s.split()) for s in all_sentences]
            avg_sent_words = sum(word_counts) // len(word_counts)

        # Formality heuristic
        formal_markers = ["regards", "sincerely", "respectfully", "pleased", "attached", "discuss"]
        casual_markers = ["hey", "cheers", "thanks!", "awesome", "cool", "super"]
        
        all_text_lower = " ".join(email_texts).lower()
        f_count = sum(1 for m in formal_markers if m in all_text_lower)
        c_count = sum(1 for m in casual_markers if m in all_text_lower)
        
        ratio = f_count / max(f_count + c_count, 1)
        formality = round(min(0.95, max(0.35, 0.5 + (ratio - 0.5) * 0.4)), 2)

        return EmailStyleMetrics(
            formality=formality,
            avg_length_chars=avg_len,
            avg_sentence_length_words=avg_sent_words,
            uses_bullet_points=any("•" in t or "- " in t for t in email_texts)
        )

    @classmethod
    def analyze_linkedin_posts(cls, post_texts: List[str]) -> LinkedInStyleMetrics:
        if not post_texts:
            return LinkedInStyleMetrics()

        total_chars = sum(len(p) for p in post_texts)
        avg_len = total_chars // len(post_texts)

        # Hashtags
        total_hashtags = sum(len(re.findall(r"#\w+", p)) for p in post_texts)
        avg_hashtags = round(total_hashtags / len(post_texts))

        # Emojis count (approximated via unicode ranges)
        emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
        total_emojis = sum(len(emoji_pattern.findall(p)) for p in post_texts)
        emoji_freq = round(total_emojis / max(total_chars, 1), 3)

        return LinkedInStyleMetrics(
            avg_length_chars=avg_len,
            typical_hashtag_count=avg_hashtags or 4,
            emoji_frequency=emoji_freq
        )
