from fastapi import APIRouter
from typing import Dict, Any

try:
    from backend.models.decision_base import DecisionRequest, DecisionResponse
    from backend.models.decision_runtime import get_decision_model
except ImportError:
    from models.decision_base import DecisionRequest, DecisionResponse
    from models.decision_runtime import get_decision_model

router = APIRouter(prefix="/api", tags=["decision"])

@router.post("/decision", response_model=DecisionResponse)
async def make_decision(req: DecisionRequest):
    """
    Dedicated System-1 Decision Endpoint.
    Executes bounded typed decisions via local Laya PyTorch model:
    - Should we query Gmail? [yes: 0.94, no: 0.06]
    - Should we query Calendar? [yes: 0.81, no: 0.19]
    - Is evidence sufficient to generate? [yes: 0.93, no: 0.07]
    Sub-2ms execution time, zero text generation overhead.
    """
    model = get_decision_model()
    response = model.decide(
        state=req.state,
        question=req.question,
        options=req.options or ["yes", "no"]
    )
    return response
