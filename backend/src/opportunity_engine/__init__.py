# Next Best Opportunity Engine: detect, score, rank, recommend
from src.opportunity_engine.opportunity_detector import detect_opportunities
from src.opportunity_engine.opportunity_ranker import rank_opportunities
from src.opportunity_engine.recommendation_engine import get_recommendations
from src.opportunity_engine.opportunity_store import store_recommendations, get_recommendations_cached
from src.opportunity_engine.opportunity_scorer import score_opportunities, score_single_opportunity
from src.opportunity_engine.models.opportunity import Opportunity
from src.opportunity_engine.models.opportunity_score import OpportunityScore

__all__ = [
    "detect_opportunities",
    "rank_opportunities",
    "get_recommendations",
    "store_recommendations",
    "get_recommendations_cached",
    "score_opportunities",
    "score_single_opportunity",
    "Opportunity",
    "OpportunityScore",
]
