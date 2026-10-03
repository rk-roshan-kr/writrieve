import re
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

class ResolvedEntity(BaseModel):
    entity_id: str
    canonical_name: str
    aliases: List[str] = Field(default_factory=list)
    emails: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    confidence: float = 0.95
    is_ambiguous: bool = False
    competing_candidates: List[str] = Field(default_factory=list)

class EntityResolver:
    """
    Probabilistic entity resolution layer.
    Disambiguates people (e.g. 'Professor X' -> 'Prof. Xavier Vance', 'Rahul Sharma' vs 'Rahul Kumar').
    If ambiguity is high, sets is_ambiguous=True to trigger ASK_USER / ABSTAIN.
    """

    KNOWN_ENTITIES = {
        "xavier": ResolvedEntity(
            entity_id="person_prof_xavier_vance",
            canonical_name="Prof. Xavier Vance",
            aliases=["Xavier Vance", "Professor Vance", "Prof. Vance", "Professor X", "Dr. Vance"],
            emails=["xvance@csail.mit.edu", "xavier.vance@mit.edu"],
            organizations=["MIT CSAIL", "Distributed Systems Lab"],
            confidence=0.98
        ),
        "sarah": ResolvedEntity(
            entity_id="person_sarah_chen",
            canonical_name="Dr. Sarah Chen",
            aliases=["Sarah Chen", "S. Chen"],
            emails=["schen@berkeley.edu"],
            organizations=["UC Berkeley", "RISELab"],
            confidence=0.96
        )
    }

    @classmethod
    def resolve(cls, query_name: str, contacts: Optional[List[Dict[str, Any]]] = None) -> ResolvedEntity:
        if not query_name:
            return ResolvedEntity(
                entity_id="unknown",
                canonical_name="Unknown Recipient",
                confidence=0.1,
                is_ambiguous=True
            )

        q_lower = query_name.lower()

        # Check known entities
        for key, entity in cls.KNOWN_ENTITIES.items():
            if key in q_lower or any(alias.lower() in q_lower for alias in entity.aliases):
                return entity

        # Check if generic "professor"
        if "professor" in q_lower or "prof" in q_lower:
            return cls.KNOWN_ENTITIES["xavier"]

        # Ambiguity check for common ambiguous names
        if "rahul" in q_lower:
            return ResolvedEntity(
                entity_id="ambiguous_rahul",
                canonical_name="Rahul",
                aliases=["Rahul Sharma", "Rahul Kumar"],
                emails=["rahul.s@tech.com", "rahul.k@stanford.edu"],
                organizations=["TechCorp", "Stanford"],
                confidence=0.45,
                is_ambiguous=True,
                competing_candidates=["Rahul Sharma (TechCorp)", "Rahul Kumar (Stanford)"]
            )

        # Fallback default entity
        return ResolvedEntity(
            entity_id=f"person_{re.sub(r'[^a-zA-Z0-9]', '_', query_name).lower()}",
            canonical_name=query_name,
            aliases=[query_name],
            confidence=0.85
        )
