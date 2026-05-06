"""
SERVICE: gpt_companion_service
PURPOSE: GPT Companion integration - guide and explainer mode
ENCODING: UTF-8 WITHOUT BOM

GPT acts as a guide and explainer. Execution always happens in SOAR backend.
GPT NEVER executes actions, only explains and suggests.

CRITICAL RULE: GPT never executes. All execution happens in SOAR backend.
"""

from typing import Optional, Dict, Any, List
import os
from enum import Enum

***REMOVED*** Optional OpenAI import (for GPT Companion feature)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None


class GPTCompanionMode(Enum):
    """GPT Companion modes"""
    GUIDE = "guide"  ***REMOVED*** Explains features, suggests next steps
    EXPLAINER = "explainer"  ***REMOVED*** Explains "Why this account?" in natural language
    STRATEGY = "strategy"  ***REMOVED*** Suggests market exploration strategies


class GPTCompanionService:
    """Service for GPT Companion integration"""
    
    def __init__(self):
        ***REMOVED*** Initialize OpenAI client (if API key available and openai package installed)
        self.client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.client = openai.OpenAI(api_key=api_key)
                except Exception:
                    self.client = None
    
    def get_guidance(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get guidance from GPT Companion.
        
        Mode: GUIDE
        Purpose: Explains features, suggests next steps
        
        CRITICAL: GPT never executes. Only explains.
        """
        if not self.client:
            return {
                "mode": GPTCompanionMode.GUIDE.value,
                "response": "GPT Companion is not configured. Please set OPENAI_API_KEY environment variable.",
                "suggested_actions": [],
                "execution_required": False
            }
        
        system_prompt = """You are SOAR B2B's GPT Companion, a guide and explainer.
        
CRITICAL RULES:
1. You NEVER execute actions. All execution happens in the SOAR backend.
2. You ONLY explain, guide, and suggest.
3. When suggesting actions, always mention they will be executed by the SOAR backend, not by you.

Your role:
- Explain SOAR B2B features
- Suggest next steps for users
- Guide users through the platform
- Answer questions about how things work

Remember: You are a GUIDE, not an executor."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            gpt_response = response.choices[0].message.content
            
            ***REMOVED*** Extract suggested actions (if any) - but mark as non-executable by GPT
            suggested_actions = self._extract_suggestions(gpt_response)
            
            return {
                "mode": GPTCompanionMode.GUIDE.value,
                "response": gpt_response,
                "suggested_actions": suggested_actions,
                "execution_required": False,  ***REMOVED*** GPT never executes
                "execution_note": "All actions must be executed through SOAR B2B backend API, not by GPT."
            }
        except Exception as e:
            return {
                "mode": GPTCompanionMode.GUIDE.value,
                "response": f"Error getting guidance: {str(e)}",
                "suggested_actions": [],
                "execution_required": False
            }
    
    def explain_target(
        self,
        target_trace: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Explain "Why this account?" in natural language.
        
        Mode: EXPLAINER
        Purpose: Converts trace data into human-readable explanation
        
        CRITICAL: GPT never executes. Only explains existing trace data.
        """
        if not self.client:
            return {
                "mode": GPTCompanionMode.EXPLAINER.value,
                "explanation": "GPT Companion is not configured. Please view the trace data directly.",
                "execution_required": False
            }
        
        system_prompt = """You are SOAR B2B's Explainability Companion.
        
Your role:
- Explain "Why this account?" in natural, business-friendly language
- Convert technical trace data into clear explanations
- Highlight key reasons why this account matches

CRITICAL: You are explaining EXISTING trace data. You never execute or modify anything.
All trace data comes from SOAR backend calculations."""
        
        user_prompt = f"""Explain why this account was matched:

Overall Score: {target_trace.get('overall_score', 0)}
Signals Used: {target_trace.get('explanation', {}).get('signals_used', [])}
Location Affinity: {target_trace.get('explanation', {}).get('location_affinity', {})}
Confidence: {target_trace.get('confidence_level', 'medium')}

Provide a clear, concise explanation in 2-3 sentences."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            explanation = response.choices[0].message.content
            
            return {
                "mode": GPTCompanionMode.EXPLAINER.value,
                "explanation": explanation,
                "execution_required": False,
                "trace_data": target_trace  ***REMOVED*** Include original trace for reference
            }
        except Exception as e:
            return {
                "mode": GPTCompanionMode.EXPLAINER.value,
                "explanation": f"Error generating explanation: {str(e)}",
                "execution_required": False
            }
    
    def suggest_strategy(
        self,
        market_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest market exploration strategies.
        
        Mode: STRATEGY
        Purpose: Suggests strategies based on market context
        
        CRITICAL: GPT suggests only. Execution happens in SOAR backend.
        """
        if not self.client:
            return {
                "mode": GPTCompanionMode.STRATEGY.value,
                "strategies": [],
                "execution_required": False
            }
        
        system_prompt = """You are SOAR B2B's Strategy Companion.
        
Your role:
- Suggest market exploration strategies
- Recommend persona targeting approaches
- Advise on location affinity settings

CRITICAL: You SUGGEST strategies. All execution happens in SOAR backend.
Your suggestions will be implemented through SOAR B2B API endpoints."""
        
        user_prompt = f"""Suggest market exploration strategies based on this context:

{market_context}

Provide 3-5 actionable strategy suggestions."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            strategy_text = response.choices[0].message.content
            strategies = self._extract_strategies(strategy_text)
            
            return {
                "mode": GPTCompanionMode.STRATEGY.value,
                "strategies": strategies,
                "full_response": strategy_text,
                "execution_required": False,
                "execution_note": "Strategies should be executed through SOAR B2B backend API."
            }
        except Exception as e:
            return {
                "mode": GPTCompanionMode.STRATEGY.value,
                "strategies": [],
                "error": str(e),
                "execution_required": False
            }
    
    def _extract_suggestions(self, text: str) -> List[str]:
        """Extract suggested actions from GPT response"""
        ***REMOVED*** Simple extraction (can be enhanced)
        suggestions = []
        lines = text.split("\n")
        for line in lines:
            if line.strip().startswith("-") or line.strip().startswith("*") or line.strip()[0].isdigit():
                suggestions.append(line.strip())
        return suggestions[:5]  ***REMOVED*** Limit to 5 suggestions
    
    def _extract_strategies(self, text: str) -> List[str]:
        """Extract strategy suggestions from GPT response"""
        ***REMOVED*** Similar to _extract_suggestions
        strategies = []
        lines = text.split("\n")
        for line in lines:
            if line.strip().startswith("-") or line.strip().startswith("*") or line.strip()[0].isdigit():
                strategies.append(line.strip())
        return strategies[:5]  ***REMOVED*** Limit to 5 strategies
