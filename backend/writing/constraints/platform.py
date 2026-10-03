from typing import Tuple

class PlatformConstraints:
    """
    Hard platform constraints (character caps, formatting rules).
    """

    CAPS = {
        "linkedin": 3000,
        "email": 10000,
        "generic": 5000
    }

    @classmethod
    def validate(cls, text: str, platform: str) -> Tuple[bool, str]:
        cap = cls.CAPS.get(platform.lower(), 5000)
        char_count = len(text)
        if char_count > cap:
            return False, f"Character count {char_count} exceeds {platform} hard limit of {cap} characters."
        return True, f"Character count {char_count} within {platform} limit ({cap} chars)."
