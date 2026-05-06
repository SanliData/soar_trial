"""
SERVICE: web_acquisition.compliance
PURPOSE: Compliance guardrails for web acquisition
ENCODING: UTF-8 WITHOUT BOM

Implements sources policy, blocklist, and rate limiting.
"""

from typing import List, Set, Dict, Any
import re


***REMOVED*** Restricted domains that should NOT be scraped by default
RESTRICTED_DOMAINS: Set[str] = {
    "linkedin.com",
    "www.linkedin.com",
    "facebook.com",
    "www.facebook.com",
    "twitter.com",
    "www.twitter.com",
    "x.com",
    "www.x.com",
    "instagram.com",
    "www.instagram.com",
    "whatsapp.com",
    "telegram.org",
    ***REMOVED*** Add other restricted platforms
}

***REMOVED*** Official sources whitelist (for "official_only" policy)
OFFICIAL_SOURCES: Set[str] = {
    ***REMOVED*** Government domains
    "gov.tr",
    "gov.uk",
    "gov.us",
    "europa.eu",
    ***REMOVED*** Municipality domains
    "belediyeler.gov.tr",
    ***REMOVED*** Chamber of commerce
    "tobb.org.tr",
    "chamber.com",
    ***REMOVED*** Company websites are allowed (not in whitelist but checked separately)
}

***REMOVED*** Public web directories (allowed in "public_web" policy)
PUBLIC_DIRECTORIES: Set[str] = {
    "google.com",
    "bing.com",
    "yellowpages.com",
    "yelp.com",
    ***REMOVED*** Add other public directories
}


class SourcesPolicy:
    """
    Sources policy enforcement.
    """
    
    OFFICIAL_ONLY = "official_only"
    PUBLIC_WEB = "public_web"
    
    @staticmethod
    def is_restricted(domain: str) -> bool:
        """
        Check if domain is in restricted blocklist.
        
        Args:
            domain: Domain name to check
            
        Returns:
            True if domain is restricted
        """
        domain_lower = domain.lower().strip()
        
        ***REMOVED*** Check exact match
        if domain_lower in RESTRICTED_DOMAINS:
            return True
        
        ***REMOVED*** Check subdomain match (e.g., "jobs.linkedin.com")
        for restricted in RESTRICTED_DOMAINS:
            if domain_lower.endswith(f".{restricted}") or domain_lower == restricted:
                return True
        
        return False
    
    @staticmethod
    def is_official_source(domain: str) -> bool:
        """
        Check if domain is an official source (government, municipality, chamber).
        
        Args:
            domain: Domain name to check
            
        Returns:
            True if domain is an official source
        """
        domain_lower = domain.lower().strip()
        
        ***REMOVED*** Check exact match
        if domain_lower in OFFICIAL_SOURCES:
            return True
        
        ***REMOVED*** Check if ends with official source domain
        for official in OFFICIAL_SOURCES:
            if domain_lower.endswith(f".{official}") or domain_lower == official:
                return True
        
        return False
    
    @staticmethod
    def is_company_website(domain: str) -> bool:
        """
        Check if domain appears to be a company website.
        Heuristic: not in restricted list, not a known social media/platform.
        
        Args:
            domain: Domain name to check
            
        Returns:
            True if domain appears to be a company website
        """
        if SourcesPolicy.is_restricted(domain):
            return False
        
        ***REMOVED*** Company websites typically don't have common platform patterns
        platform_patterns = [
            r"^(www\.)?(linkedin|facebook|twitter|x|instagram|whatsapp)",
            r"\.(blog|medium|substack)\.com$",
        ]
        
        domain_lower = domain.lower()
        for pattern in platform_patterns:
            if re.search(pattern, domain_lower):
                return False
        
        return True
    
    @staticmethod
    def is_allowed(domain: str, policy: str) -> bool:
        """
        Check if domain is allowed under the given policy.
        
        Args:
            domain: Domain name to check
            policy: Sources policy ("official_only" or "public_web")
            
        Returns:
            True if domain is allowed
        """
        ***REMOVED*** Always block restricted domains
        if SourcesPolicy.is_restricted(domain):
            return False
        
        if policy == SourcesPolicy.OFFICIAL_ONLY:
            ***REMOVED*** Only official sources + company websites
            return SourcesPolicy.is_official_source(domain) or SourcesPolicy.is_company_website(domain)
        
        elif policy == SourcesPolicy.PUBLIC_WEB:
            ***REMOVED*** Official sources + company websites + public directories
            return (
                SourcesPolicy.is_official_source(domain) or
                SourcesPolicy.is_company_website(domain) or
                any(domain.lower().endswith(f".{d}") or domain.lower() == d for d in PUBLIC_DIRECTORIES)
            )
        
        ***REMOVED*** Default: deny unknown policies
        return False
    
    @staticmethod
    def validate_sources_policy(policy: str) -> bool:
        """
        Validate that sources policy is one of the allowed values.
        
        Args:
            policy: Sources policy string
            
        Returns:
            True if policy is valid
        """
        return policy in [SourcesPolicy.OFFICIAL_ONLY, SourcesPolicy.PUBLIC_WEB]


class RateLimiter:
    """
    Per-domain rate limiting.
    Simple in-memory implementation (can be replaced with Redis for production).
    """
    
    def __init__(self):
        """Initialize rate limiter."""
        self._domain_requests: Dict[str, List[float]] = {}
        self._max_requests_per_minute = 10
        self._cleanup_interval = 60.0  ***REMOVED*** seconds
    
    def is_allowed(self, domain: str) -> bool:
        """
        Check if request to domain is allowed under rate limit.
        
        Args:
            domain: Domain name
            
        Returns:
            True if request is allowed
        """
        import time
        
        domain_lower = domain.lower()
        current_time = time.time()
        
        ***REMOVED*** Get or create request history for domain
        if domain_lower not in self._domain_requests:
            self._domain_requests[domain_lower] = []
        
        ***REMOVED*** Clean old requests (older than 1 minute)
        self._domain_requests[domain_lower] = [
            req_time
            for req_time in self._domain_requests[domain_lower]
            if current_time - req_time < self._cleanup_interval
        ]
        
        ***REMOVED*** Check if limit exceeded
        if len(self._domain_requests[domain_lower]) >= self._max_requests_per_minute:
            return False
        
        ***REMOVED*** Record this request
        self._domain_requests[domain_lower].append(current_time)
        return True
    
    def reset(self, domain: str = None):
        """
        Reset rate limit for domain or all domains.
        
        Args:
            domain: Domain to reset (None = all domains)
        """
        if domain:
            domain_lower = domain.lower()
            if domain_lower in self._domain_requests:
                del self._domain_requests[domain_lower]
        else:
            self._domain_requests.clear()


***REMOVED*** Global rate limiter instance
_global_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    return _global_rate_limiter
