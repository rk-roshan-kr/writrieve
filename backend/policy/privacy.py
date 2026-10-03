import re

# Regular expressions for sensitive personal data masking
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PASSWORD_TOKEN_REGEX = re.compile(r"(?i)(?:password|secret|bearer\s+|api[_-]?key)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})")

class PrivacyGuard:
    """
    Sanitizes retrieved candidate text to ensure credentials, tokens, or financial numbers
    never leak into the LLM context or user logs.
    """

    @classmethod
    def sanitize(cls, text: str) -> str:
        if not text:
            return ""
        sanitized = CREDIT_CARD_REGEX.sub("[REDACTED_CARD]", text)
        sanitized = SSN_REGEX.sub("[REDACTED_SSN]", sanitized)
        sanitized = PASSWORD_TOKEN_REGEX.sub(r"password: [REDACTED_SECRET]", sanitized)
        return sanitized
