"""ExecutionContext for managing request-scoped state."""
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ExecutionContext(BaseModel):
    """
    Manages state for a single request/interaction.
    Includes user context, memory snapshots, and safety flags.
    """
    session_id: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    # Placeholder for future state
    # last_interaction: datetime
    # safety_level: int
