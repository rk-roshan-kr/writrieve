from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EmailStyleMetrics(BaseModel):
    formality: float = 0.72                     # 0.0 (super casual) to 1.0 (academic/formal)
    avg_length_chars: int = 420                # Typical concise email
    avg_sentence_length_words: int = 16
    greeting_patterns: List[str] = Field(default_factory=lambda: ["Dear Professor {name},", "Hi {name},", "Hello {name},"])
    closing_patterns: List[str] = Field(default_factory=lambda: ["Best regards,", "Best,", "Warmly,"])
    uses_bullet_points: bool = True
    signature_format: str = "{user_name}\nGraduate Researcher, Distributed Systems Lab"

class LinkedInStyleMetrics(BaseModel):
    avg_length_chars: int = 1140               # Typical post length (well below 3000 cap)
    hard_char_limit: int = 3000
    avg_paragraph_sentences: float = 2.0       # Snappy 1-3 sentence paragraphs
    emoji_frequency: float = 0.08              # Low, deliberate emoji usage
    hashtag_frequency: float = 0.85
    typical_hashtag_count: int = 4
    hook_style: str = "personal_declarative"   # "Excited to share", "Reflecting on", etc.
    cta_frequency: float = 0.20                # Occasional discussion prompt
    signoff_frequency: float = 0.02            # Typically no formal signoff

class PersonalWritingProfile(BaseModel):
    user_id: str = "write4u_default_user"
    user_name: str = "Roshan"
    email: EmailStyleMetrics = Field(default_factory=EmailStyleMetrics)
    linkedin: LinkedInStyleMetrics = Field(default_factory=LinkedInStyleMetrics)
    active_medium: str = "email"

    def get_active_metrics(self) -> BaseModel:
        if self.active_medium == "linkedin":
            return self.linkedin
        return self.email
