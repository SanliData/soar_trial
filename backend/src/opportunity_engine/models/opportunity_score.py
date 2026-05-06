"""
OPPORTUNITY_ENGINE: opportunity score model
PURPOSE: Scored opportunity with recommended persona and confidence
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OpportunityScore(BaseModel):
    """Opportunity with score (0.0-1.0), recommended_persona, confidence."""
    company: str
    company_id: Optional[int] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    score: float = Field(..., ge=0.0, le=1.0)
    recommended_persona: Optional[str] = Field(None, description="Best target role: CEO, CTO, Founder, VP Operations, Procurement Director")
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    signals: List[str] = Field(default_factory=list)
    score_breakdown: Dict[str, float] = Field(default_factory=dict, description="industry_reply, persona_success, similarity, market_signals, engagement")
