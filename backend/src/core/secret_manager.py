"""
CORE: secret_manager
PURPOSE: Google Cloud Secret Manager integration with fallback to environment variables
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

***REMOVED*** Try to import Secret Manager client
try:
    from google.cloud import secretmanager
    SECRET_MANAGER_AVAILABLE = True
except ImportError:
    SECRET_MANAGER_AVAILABLE = False
    secretmanager = None


class SecretManager:
    """
    Service for reading secrets from Google Cloud Secret Manager with fallback to environment variables.
    
    Priority:
    1. Google Cloud Secret Manager (production)
    2. Environment variables (development/local)
    
    Usage:
        secret_mgr = SecretManager()
        jwt_secret = secret_mgr.get_secret("JWT_SECRET")
    """
    
    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize Secret Manager.
        
        Args:
            project_id: GCP project ID. If None, reads from GOOGLE_CLOUD_PROJECT_ID env var.
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.client = None
        
        ***REMOVED*** Initialize Secret Manager client if available and in production
        if SECRET_MANAGER_AVAILABLE and self.project_id:
            try:
                ***REMOVED*** Check if we're in a GCP environment (Cloud Run, GCE, etc.)
                ***REMOVED*** Cloud Run sets K_SERVICE, GCE sets GCE_METADATA_HOST
                is_gcp_env = (
                    os.getenv("K_SERVICE") is not None or  ***REMOVED*** Cloud Run
                    os.getenv("GCE_METADATA_HOST") is not None or  ***REMOVED*** GCE
                    os.getenv("GOOGLE_CLOUD_PROJECT") is not None  ***REMOVED*** Any GCP service
                )
                
                if is_gcp_env:
                    self.client = secretmanager.SecretManagerServiceClient()
                    logger.info(f"Secret Manager initialized for project: {self.project_id}")
                else:
                    logger.info("Not in GCP environment, using environment variable fallback")
            except Exception as e:
                logger.warning(f"Failed to initialize Secret Manager client: {str(e)}. Using env var fallback.")
                self.client = None
        else:
            if not SECRET_MANAGER_AVAILABLE:
                logger.info("google-cloud-secret-manager not available. Using env var fallback.")
            if not self.project_id:
                logger.info("GOOGLE_CLOUD_PROJECT_ID not set. Using env var fallback.")
    
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret value from Secret Manager or environment variable.
        
        Args:
            secret_name: Name of the secret (without project/path prefix)
            default: Default value if secret not found (optional)
        
        Returns:
            Secret value as string, or default/None if not found
        """
        ***REMOVED*** Try Secret Manager first (production)
        if self.client and self.project_id:
            try:
                secret_path = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
                response = self.client.access_secret_version(request={"name": secret_path})
                secret_value = response.payload.data.decode("UTF-8")
                logger.debug(f"Retrieved secret '{secret_name}' from Secret Manager")
                return secret_value
            except Exception as e:
                logger.warning(
                    f"Failed to retrieve secret '{secret_name}' from Secret Manager: {str(e)}. "
                    "Falling back to environment variable."
                )
        
        ***REMOVED*** Fallback to environment variable (development/local)
        env_value = os.getenv(secret_name, default)
        if env_value:
            logger.debug(f"Retrieved secret '{secret_name}' from environment variable")
        else:
            logger.warning(f"Secret '{secret_name}' not found in Secret Manager or environment variables")
        
        return env_value
    
    def is_available(self) -> bool:
        """Check if Secret Manager is available and configured."""
        return self.client is not None and self.project_id is not None


***REMOVED*** Singleton instance
_secret_manager_instance = None


def get_secret_manager(project_id: Optional[str] = None) -> SecretManager:
    """
    Get or create SecretManager singleton instance.
    
    Args:
        project_id: Optional project ID override
    
    Returns:
        SecretManager instance
    """
    global _secret_manager_instance
    if _secret_manager_instance is None:
        _secret_manager_instance = SecretManager(project_id=project_id)
    return _secret_manager_instance
