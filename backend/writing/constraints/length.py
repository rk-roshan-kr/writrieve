from typing import Tuple

class LengthConstraints:
    """
    Validates generated text against the blueprint target and boundaries.
    """

    @classmethod
    def evaluate(cls, text: str, min_chars: int, max_chars: int, target_chars: int) -> Tuple[bool, float, str]:
        char_count = len(text)
        if char_count < min_chars:
            return False, 0.4, f"Text length ({char_count} chars) is below minimum required ({min_chars} chars)."
        if char_count > max_chars:
            return False, 0.4, f"Text length ({char_count} chars) exceeds maximum allowed ({max_chars} chars)."

        # Deviation from ideal target
        deviation = abs(char_count - target_chars) / max(target_chars, 1)
        score = max(0.6, round(1.0 - (deviation * 0.5), 2))
        return True, score, f"Length {char_count} chars is optimal (target: {target_chars})."
