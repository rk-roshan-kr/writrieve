from typing import Set, Tuple

# Strict read-only allowed tool actions for Write4U
ALLOWED_ACTIONS: Set[str] = {
    "GMAIL_LIST_MESSAGES",
    "GMAIL_FETCH_MESSAGE",
    "GOOGLECALENDAR_LIST_EVENTS",
    "GOOGLEDRIVE_LIST_FILES",
    "GOOGLEDRIVE_FETCH_FILE",
    "GITHUB_LIST_COMMITS",
    "LINKEDIN_FETCH_PROFILE"
}

FORBIDDEN_ACTIONS: Set[str] = {
    "GMAIL_SEND_EMAIL",
    "GMAIL_DELETE_MESSAGE",
    "GOOGLECALENDAR_DELETE_EVENT",
    "GOOGLECALENDAR_CREATE_EVENT",
    "GOOGLEDRIVE_DELETE_FILE",
    "GITHUB_PUSH_CODE"
}

class PolicyPermissions:
    """
    Deterministic security gate enforcing read-only boundary over external connectors (e.g. Composio).
    Prevents prompt injection or rogue agents from executing destructive write operations.
    """

    @classmethod
    def is_action_allowed(cls, action_name: str) -> Tuple[bool, str]:
        upper_act = action_name.upper()
        if upper_act in FORBIDDEN_ACTIONS:
            return False, f"Action '{action_name}' is explicitly forbidden by Write4U safety policy."
        if "DELETE" in upper_act or "MODIFY" in upper_act or "SEND" in upper_act:
            return False, f"Destructive/Mutating action '{action_name}' is blocked."
        return True, "Action allowed (read-only verification)."

    @classmethod
    def filter_allowed_sources(cls, requested_sources: Set[str]) -> Set[str]:
        # Sources permitted for personal context reading
        valid = {"gmail", "calendar", "googlecalendar", "drive", "googledrive", "contacts", "linkedin", "github"}
        return {s.lower() for s in requested_sources if s.lower() in valid}
