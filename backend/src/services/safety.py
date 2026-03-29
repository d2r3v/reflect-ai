"""Safety Engine service.

Responsible for:
- Classifying risk level (low, medium, high, critical)
- Selecting appropriate response policy
- Enforcing deterministic bypass for critical-risk situations
"""

from enum import Enum


class RiskLevel(str, Enum):
    """Risk classification levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyService:
    """Service for safety classification and policy routing."""
    
    def __init__(self):
        """Initialize safety service."""
        pass
    
    async def classify_risk(self, user_message: str) -> RiskLevel:
        """Classify the risk level of user input.
        
        Args:
            user_message: The user's input message
            
        Returns:
            RiskLevel enum value
        """
        # TODO: Implement risk classification logic
        raise NotImplementedError("Risk classification not yet implemented")
    
    async def get_crisis_response(self) -> str:
        """Return deterministic, hardcoded crisis support response.
        
        This is used for critical-risk situations and must never use
        dynamic LLM generation.
        
        Returns:
            Hardcoded crisis support message with resources
        """
        # TODO: Implement hardcoded crisis response
        raise NotImplementedError("Crisis response not yet implemented")
