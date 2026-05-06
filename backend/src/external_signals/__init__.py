"""
EXTERNAL_SIGNALS: Collectors for hiring spike, funding, job postings, company news.
PURPOSE: Store signals in Redis and feed market_signals engine
"""
from src.external_signals.linkedin_signal_collector import collect_linkedin_signals
from src.external_signals.funding_signal_collector import collect_funding_signals
from src.external_signals.job_posting_signal_collector import collect_job_posting_signals
from src.external_signals.company_news_collector import collect_company_news_signals

__all__ = [
    "collect_linkedin_signals",
    "collect_funding_signals",
    "collect_job_posting_signals",
    "collect_company_news_signals",
]
