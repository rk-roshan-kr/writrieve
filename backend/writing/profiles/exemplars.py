from typing import List, Dict, Any
from pydantic import BaseModel

class WritingExemplar(BaseModel):
    id: str
    medium: str          # "email" or "linkedin"
    category: str        # "professional_followup", "meeting_request", "conference_award", "research_update"
    length_type: str     # "short", "medium", "long"
    sample_text: str
    key_stylistic_features: List[str]

class ExemplarStore:
    """
    Maintains representative writing exemplars from the user's historical writing.
    Provides style compression: passes 2-3 targeted examples to the generator rather than 50 raw posts.
    """

    EXEMPLARS: List[WritingExemplar] = [
        WritingExemplar(
            id="ex_email_followup",
            medium="email",
            category="professional_followup",
            length_type="medium",
            sample_text=(
                "Dear Professor Vance,\n\n"
                "Thank you for the stimulating discussion during the Distributed Systems session at CCNCPS. "
                "I greatly enjoyed exchanging thoughts on our FieldChain architecture, especially your insights regarding Byzantine quorum degradation under network partitions.\n\n"
                "As mentioned, our latest benchmarks demonstrate 19.4k TPS across 128 nodes with 42ms finality. "
                "I have attached the updated draft for your reference.\n\n"
                "Would you be open to a brief 15-minute call next Thursday or Friday to discuss potential next steps for extending the consensus evaluation?\n\n"
                "Best regards,\n"
                "Roshan\nGraduate Researcher, Distributed Systems Lab"
            ),
            key_stylistic_features=[
                "Explicit greeting with formal title",
                "Warm opening referencing shared in-person conversation",
                "Concise technical paragraph with specific numerical benchmark metrics",
                "Concrete, low-friction scheduling call-to-action (specific days and duration)",
                "Standard professional signoff with affiliation"
            ]
        ),
        WritingExemplar(
            id="ex_linkedin_award",
            medium="linkedin",
            category="conference_award",
            length_type="medium",
            sample_text=(
                "Thrilled to share that our paper 'FieldChain: Resilient Consensus via Adaptive Sharding' "
                "was awarded Best Poster Runner-Up in the Distributed Systems track at CCNCPS 2026 in San Francisco!\n\n"
                "In our latest testbed benchmarks, FieldChain achieved 19.4k TPS across 128 nodes with 42ms finality under network partitions.\n\n"
                "Huge thanks to Prof. Xavier Vance and my lab collaborators for the invaluable discussions on Byzantine consensus limits.\n\n"
                "Code and reproduction benchmarks are fully open-source on GitHub.\n\n"
                "#DistributedSystems #Consensus #Research #CCNCPS #OpenSource"
            ),
            key_stylistic_features=[
                "Declarative hook announcing achievement",
                "Short 1-2 sentence paragraphs with whitespace",
                "Concrete metrics: 19.4k TPS, 128 nodes, 42ms finality",
                "Generous attribution to advisors and lab collaborators",
                "Open-source link mention",
                "Curated 4-5 relevant technical hashtags"
            ]
        )
    ]

    @classmethod
    def get_exemplars(cls, medium: str, category: str = None) -> List[WritingExemplar]:
        matches = [e for e in cls.EXEMPLARS if e.medium == medium]
        if category:
            cat_matches = [e for e in matches if e.category == category]
            if cat_matches:
                return cat_matches
        return matches[:2]
