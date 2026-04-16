"""Safety Engine service.

Responsible for:
- Classifying risk level (low, medium, high, critical)
- Selecting appropriate response policy
- Enforcing deterministic bypass for critical-risk situations
"""

import re
from enum import Enum
from typing import Dict, List
from src.core.context.execution import ResponseMode


class RiskLevel(str, Enum):
    """Risk classification levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyService:
    """Service for safety classification and policy routing."""
    
    # Simple deterministic v1 rules
    CRITICAL_KEYWORDS = ["kill myself", "end it all", "end my life", "want to die"]
    HIGH_KEYWORDS = ["hurt myself", "don't want to be here", "better off dead", "no reason to live"]
    MEDIUM_KEYWORDS = ["so alone", "can't cope", "pointless", "nobody cares", "give up", "giving up"]

    def __init__(self):
        """Initialize safety service."""
        pass
        
    def _matches_any(self, text: str, patterns: List[str]) -> bool:
        """Check if any keyword phrases are in the text."""
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in patterns)

    async def classify_risk(self, user_message: str) -> RiskLevel:
        """Classify the risk level of user input.
        
        Args:
            user_message: The user's input message
            
        Returns:
            RiskLevel enum value
        """
        # Critical priority checking first
        if self._matches_any(user_message, self.CRITICAL_KEYWORDS):
            return RiskLevel.CRITICAL
            
        if self._matches_any(user_message, self.HIGH_KEYWORDS):
            return RiskLevel.HIGH
            
        if self._matches_any(user_message, self.MEDIUM_KEYWORDS):
            return RiskLevel.MEDIUM
            
        return RiskLevel.LOW
        
    def map_risk_to_mode(self, risk: RiskLevel) -> ResponseMode:
        """Map the classified risk level to an execution response mode."""
        mapping: Dict[RiskLevel, ResponseMode] = {
            RiskLevel.LOW: ResponseMode.REFLECT,
            RiskLevel.MEDIUM: ResponseMode.VENT,
            RiskLevel.HIGH: ResponseMode.GROUNDING,
            RiskLevel.CRITICAL: ResponseMode.CRISIS,
        }
        return mapping[risk]
    
    async def get_crisis_response(self) -> str:
        """Return deterministic, hardcoded crisis support response.
        
        This is used for critical-risk situations and must never use
        dynamic LLM generation.
        
        Returns:
            Hardcoded crisis support message with resources
        """
        return (
            "I'm really glad you said something. You matter, and I'm concerned about your safety.\n\n"
            "Please call or text 988 right now.\n\n"
            "You can also text HOME to 741741 to reach a Crisis Text Line counselor — "
            "available 24/7, free, and confidential.\n\n"
            "I can stay with you here, but I'm not a substitute for immediate professional support."
        )
