"""
SERVICE: google_ads_service
PURPOSE: Google Ads API integration for B2B targeted advertising
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
import hashlib
import base64
from typing import Dict, Optional, List, Any
from datetime import datetime

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    from google.ads.googleads.v16.enums.types.user_list_membership_status import UserListMembershipStatusEnum
    from google.ads.googleads.v16.enums.types.user_list_type import UserListTypeEnum
    from google.ads.googleads.v16.enums.types.offline_user_data_job_type import OfflineUserDataJobTypeEnum
    from google.ads.googleads.v16.enums.types.offline_user_data_job_status import OfflineUserDataJobStatusEnum
    from google.ads.googleads.v16.enums.types.campaign_status import CampaignStatusEnum
    from google.ads.googleads.v16.enums.types.advertising_channel_type import AdvertisingChannelTypeEnum
    from google.ads.googleads.v16.enums.types.ad_group_type import AdGroupTypeEnum
    from google.ads.googleads.v16.enums.types.ad_group_ad_status import AdGroupAdStatusEnum
    from google.ads.googleads.v16.resources.types.customer_user_list import CustomerUserList
    from google.ads.googleads.v16.resources.types.offline_user_data_job import OfflineUserDataJob
    from google.ads.googleads.v16.resources.types.campaign import Campaign
    from google.ads.googleads.v16.resources.types.ad_group import AdGroup
    from google.ads.googleads.v16.resources.types.ad_group_ad import AdGroupAd
    from google.ads.googleads.v16.resources.types.ad import Ad
    from google.ads.googleads.v16.common.types.offline_user_data import OfflineUserData
    from google.ads.googleads.v16.common.types.user_identifier import UserIdentifier
    from google.ads.googleads.v16.common.types.text_ad_info import TextAdInfo
    GOOGLE_ADS_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_AVAILABLE = False
    GoogleAdsClient = None
    GoogleAdsException = Exception
    UserListMembershipStatusEnum = None
    UserListTypeEnum = None
    OfflineUserDataJobTypeEnum = None
    OfflineUserDataJobStatusEnum = None
    CampaignStatusEnum = None
    AdvertisingChannelTypeEnum = None
    AdGroupTypeEnum = None
    AdGroupAdStatusEnum = None
    CustomerUserList = None
    OfflineUserDataJob = None
    Campaign = None
    AdGroup = None
    AdGroupAd = None
    Ad = None
    OfflineUserData = None
    UserIdentifier = None
    TextAdInfo = None

logger = logging.getLogger(__name__)


class GoogleAdsService:
    """
    Service for Google Ads API integration.
    Handles Customer Match, Dynamic Search Ads, and Lead Form Extensions.
    """
    
    def __init__(self):
        """Initialize Google Ads Service with configuration from environment variables."""
        self.developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
        self.client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
        self.refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
        self.manager_customer_id = os.getenv("GOOGLE_ADS_MANAGER_CUSTOMER_ID")
        self.login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
        
        # Validate required credentials
        if not all([self.developer_token, self.client_id, self.client_secret, self.refresh_token]):
            logger.warning("Google Ads credentials not fully configured. Some features may not work.")
            self.client = None
        else:
            self.client = self._initialize_client()
    
    def _initialize_client(self) -> Optional[GoogleAdsClient]:
        """
        Initialize Google Ads API client.
        Returns None if credentials are missing or initialization fails.
        """
        if not GOOGLE_ADS_AVAILABLE:
            logger.error("google-ads library not installed. Install with: pip install google-ads")
            return None
        
        try:
            # Create client using environment variables or explicit config
            # Google Ads client reads from GOOGLE_ADS_CONFIGURATION_FILE_PATH or uses explicit dict
            config = {
                "developer_token": self.developer_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "use_proto_plus": True
            }
            
            # Add manager customer ID if provided
            if self.manager_customer_id:
                config["login_customer_id"] = self.manager_customer_id
            
            client = GoogleAdsClient.load_from_dict(config)
            logger.info("Google Ads client initialized successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {str(e)}")
            return None
    
    def is_available(self) -> bool:
        """Check if Google Ads service is available and configured."""
        return self.client is not None and GOOGLE_ADS_AVAILABLE
    
    def get_customer_client(self, customer_id: str) -> Optional[Any]:
        """
        Get a customer-specific client for operations.
        
        Args:
            customer_id: Google Ads customer ID (format: XXX-XXX-XXXX)
        
        Returns:
            Customer client or None if unavailable
        """
        if not self.is_available():
            logger.error("Google Ads service not available")
            return None
        
        try:
            # Return the service for the specific customer
            return self.client.get_service("GoogleAdsService")
        except Exception as e:
            logger.error(f"Failed to get customer client for {customer_id}: {str(e)}")
            return None
    
    def create_search_campaign_with_ads(
        self,
        customer_id: str,
        user_id: int,
        campaign_name: str,
        product_info: Dict[str, Any],
        ad_data: Dict[str, Any],
        budget_amount_micros: int = 10000000,   # $10 per day default
        user_list_id: Optional[str] = None,
        conversion_strategy: str = "appointment",   # "appointment" or "direct_traffic"
        sales_site_url: Optional[str] = None,
        utm_parameters: Optional[Dict[str, str]] = None,
        locale: str = "en",
        target_coordinates: Optional[Dict[str, float]] = None   # {"latitude": float, "longitude": float} for 10m radius
    ) -> Dict[str, Any]:
        """
        Create a Google Ads Search Campaign with ads generated from Step 1 product info.
        Uses Step 8-9 ad data and Gemini API to generate 3 ad variations.
        
        Args:
            customer_id: Google Ads customer ID (format: XXX-XXX-XXXX)
            user_id: FinderOS user ID
            campaign_name: Name for the campaign
            product_info: Product information from Step 1 (name, description, category)
            ad_data: Ad data from Step 8-9 (ad_content, ad_link, etc.)
            budget_amount_micros: Daily budget in micros (1,000,000 micros = $1)
            user_list_id: Optional Customer Match user list ID for targeting
        
        Returns:
            Dictionary with campaign creation result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Ads service not available"
            }
        
        if not GOOGLE_ADS_AVAILABLE:
            return {
                "success": False,
                "error": "google-ads library not installed"
            }
        
        try:
            # Import Gemini service for ad copy generation
            from src.services.gemini_analysis_service import get_gemini_analysis_service
            
            # Store target coordinates for location targeting
            if target_coordinates:
                self._target_coordinates = target_coordinates
            
            # Remove dashes from customer ID
            customer_id_clean = customer_id.replace("-", "")
            
            # Step 1: Generate ad copy using Gemini API (locale-aware)
            gemini_service = get_gemini_analysis_service()
            ad_copy_result = gemini_service.generate_ad_copy(
                product_name=product_info.get("name", ""),
                product_description=product_info.get("description", ""),
                product_category=product_info.get("category"),
                num_variations=3,
                locale=locale
            )
            
            if not ad_copy_result.get("success"):
                logger.warning(f"Failed to generate ad copy with Gemini: {ad_copy_result.get('error')}")
                # Fallback: use ad_data from Step 8-9
                ad_variations = [
                    {
                        "headline_1": product_info.get("name", "Product")[:30],
                        "headline_2": "B2B Solution"[:30],
                        "headline_3": "Get Started"[:30],
                        "description": ad_data.get("ad_content", product_info.get("description", ""))[:90]
                    }
                ] * 3
            else:
                ad_variations = ad_copy_result.get("ad_variations", [])
            
            logger.info(f"Generated {len(ad_variations)} ad variations")
            
            # Step 2: Create Campaign
            campaign_service = self.client.get_service("CampaignService")
            campaign_operation = self.client.get_type("CampaignOperation")
            
            campaign = campaign_operation.create
            campaign.name = campaign_name
            campaign.advertising_channel_type = AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
            campaign.status = CampaignStatusEnum.CampaignStatus.PAUSED   # Start paused, activate later
            campaign.campaign_budget = f"customers/{customer_id_clean}/campaignBudgets/0"   # Will create budget first
            
            # Set targeting (Customer Match if provided)
            if user_list_id:
                campaign.targeting.customer_match.user_list = f"customers/{customer_id_clean}/customerUserLists/{user_list_id}"
            
            # Create budget first
            budget_service = self.client.get_service("CampaignBudgetService")
            budget_operation = self.client.get_type("CampaignBudgetOperation")
            
            budget = budget_operation.create
            budget.name = f"{campaign_name} Budget"
            budget.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.BudgetDeliveryMethod.STANDARD
            budget.amount_micros = budget_amount_micros
            
            budget_response = budget_service.mutate_campaign_budgets(
                customer_id=customer_id_clean,
                operations=[budget_operation]
            )
            budget_resource_name = budget_response.results[0].resource_name
            campaign.campaign_budget = budget_resource_name
            
            # Create campaign
            campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id_clean,
                operations=[campaign_operation]
            )
            campaign_resource_name = campaign_response.results[0].resource_name
            campaign_id = campaign_resource_name.split("/")[-1]
            
            logger.info(f"Campaign created: {campaign_id}")
            
            # Step 2.5: Add location targeting (if coordinates provided)
            # Note: For 10m radius targeting, we use proximity targeting
            # Google Ads API supports proximity targeting via CampaignCriterion
            if hasattr(self, '_target_coordinates') and self._target_coordinates:
                try:
                    if GOOGLE_ADS_AVAILABLE:
                        from google.ads.googleads.v16.resources.types.campaign_criterion import CampaignCriterion
                        from google.ads.googleads.v16.common.types.proximity import ProximityInfo
                        from google.ads.googleads.v16.enums.types.proximity_radius_units import ProximityRadiusUnitsEnum
                        from google.ads.googleads.v16.common.types.geo_point_info import GeoPointInfo
                        
                        criterion_service = self.client.get_service("CampaignCriterionService")
                        criterion_operation = self.client.get_type("CampaignCriterionOperation")
                        
                        criterion = criterion_operation.create
                        criterion.campaign = campaign_resource_name
                        
                        # Create proximity targeting (10m radius)
                        proximity = ProximityInfo()
                        geo_point = GeoPointInfo()
                        geo_point.latitude_in_micro_degrees = int(self._target_coordinates["latitude"] * 1000000)
                        geo_point.longitude_in_micro_degrees = int(self._target_coordinates["longitude"] * 1000000)
                        proximity.geo_point = geo_point
                        proximity.radius = 10   # 10 meters
                        proximity.radius_units = ProximityRadiusUnitsEnum.ProximityRadiusUnits.METERS
                        
                        criterion.proximity = proximity
                        
                        criterion_response = criterion_service.mutate_campaign_criteria(
                            customer_id=customer_id_clean,
                            operations=[criterion_operation]
                        )
                        
                        logger.info(f"Location targeting added: 10m radius at ({self._target_coordinates['latitude']}, {self._target_coordinates['longitude']})")
                    
                    # Clear target coordinates
                    self._target_coordinates = None
                except Exception as e:
                    logger.warning(f"Could not add location targeting: {e}. Campaign created without location targeting.")
            
            # Step 3: Create Ad Group
            ad_group_service = self.client.get_service("AdGroupService")
            ad_group_operation = self.client.get_type("AdGroupOperation")
            
            ad_group = ad_group_operation.create
            ad_group.name = f"{campaign_name} Ad Group"
            ad_group.campaign = campaign_resource_name
            ad_group.type_ = AdGroupTypeEnum.AdGroupType.SEARCH_STANDARD
            ad_group.cpc_bid_micros = 1000000   # $1 CPC default
            
            ad_group_response = ad_group_service.mutate_ad_groups(
                customer_id=customer_id_clean,
                operations=[ad_group_operation]
            )
            ad_group_resource_name = ad_group_response.results[0].resource_name
            ad_group_id = ad_group_resource_name.split("/")[-1]
            
            logger.info(f"Ad Group created: {ad_group_id}")
            
            # Step 4: Create Ads (3 variations)
            ad_group_ad_service = self.client.get_service("AdGroupAdService")
            created_ads = []
            
            for i, variation in enumerate(ad_variations, 1):
                ad_group_ad_operation = self.client.get_type("AdGroupAdOperation")
                
                ad_group_ad = ad_group_ad_operation.create
                ad_group_ad.ad_group = ad_group_resource_name
                ad_group_ad.status = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED   # Start paused
                
                # Create text ad
                ad = ad_group_ad.ad
                ad.type_ = self.client.enums.AdTypeEnum.AdType.RESPONSIVE_SEARCH_AD
                
                # Set headlines and description
                ad.responsive_search_ad.headlines.extend([
                    self.client.get_type("AdTextAsset")(text=variation.get("headline_1", "")[:30]),
                    self.client.get_type("AdTextAsset")(text=variation.get("headline_2", "")[:30]),
                    self.client.get_type("AdTextAsset")(text=variation.get("headline_3", "")[:30])
                ])
                ad.responsive_search_ad.descriptions.extend([
                    self.client.get_type("AdTextAsset")(text=variation.get("description", "")[:90])
                ])
                
                # Set final URL based on conversion strategy
                final_url = None
                
                if conversion_strategy == "direct_traffic" and sales_site_url:
                    # Direct Traffic: Use sales site URL with UTM parameters
                    from src.services.utm_service import get_utm_service
                    utm_service = get_utm_service()
                    
                    # Generate UTM parameters if not provided
                    if not utm_parameters:
                        utm_parameters = utm_service.generate_utm_parameters(
                            campaign_id=int(campaign_id),
                            campaign_name=campaign_name,
                            region=ad_data.get("target_region"),
                            company_pool_id=ad_data.get("company_pool_id"),
                            personnel_pool_id=ad_data.get("personnel_pool_id")
                        )
                    
                    # Build tracked URL
                    final_url = utm_service.build_tracked_url(sales_site_url, utm_parameters)
                    logger.info(f"Direct Traffic: Using tracked URL with UTM parameters")
                elif conversion_strategy == "appointment":
                    # Appointment: Use Lead Form Extension (will be created separately)
                    # For now, use a placeholder that will be replaced by Lead Form Extension
                    final_url = ad_data.get("ad_link") or "https://example.com/appointment"
                    logger.info(f"Appointment: Using Lead Form Extension URL")
                else:
                    # Fallback: use ad_link from Step 8-9
                    final_url = ad_data.get("ad_link") or "https://example.com"
                
                ad.final_urls.append(final_url)
                
                # Create ad
                ad_response = ad_group_ad_service.mutate_ad_group_ads(
                    customer_id=customer_id_clean,
                    operations=[ad_group_ad_operation]
                )
                ad_resource_name = ad_response.results[0].resource_name
                ad_id = ad_resource_name.split("/")[-1]
                
                created_ads.append({
                    "ad_id": ad_id,
                    "headline_1": variation.get("headline_1"),
                    "headline_2": variation.get("headline_2"),
                    "headline_3": variation.get("headline_3"),
                    "description": variation.get("description")
                })
                
                logger.info(f"Ad {i} created: {ad_id}")
            
            return {
                "success": True,
                "message": "Search Campaign created successfully",
                "campaign_id": campaign_id,
                "campaign_resource_name": campaign_resource_name,
                "ad_group_id": ad_group_id,
                "ad_group_resource_name": ad_group_resource_name,
                "budget_resource_name": budget_resource_name,
                "ads": created_ads,
                "ad_variations_count": len(created_ads),
                "user_id": user_id,
                "campaign_name": campaign_name,
                "status": "paused"   # Campaign starts paused
            }
            
        except GoogleAdsException as e:
            error_messages = []
            for error in e.failure.errors:
                error_messages.append(f"{error.error_code.error_code}: {error.message}")
            error_msg = f"Google Ads API error: {'; '.join(error_messages)}"
            logger.error(f"Google Ads API error creating campaign: {error_msg}")
            
            # Log error to database
            try:
                from src.services.error_logging_service import get_error_logging_service
                from src.db.base import SessionLocal
                db = SessionLocal()
                try:
                    error_service = get_error_logging_service(db)
                    error_service.log_error(
                        error=e,
                        service_name="google_ads_service",
                        endpoint="create_search_campaign_with_ads",
                        user_id=user_id,
                        severity="error",
                        metadata={"customer_id": customer_id, "campaign_name": campaign_name}
                    )
                finally:
                    db.close()
            except Exception as log_error:
                logger.warning(f"Failed to log error to database: {str(log_error)}")
            
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            logger.error(f"Error creating Search Campaign: {str(e)}")
            
            # Log error to database
            try:
                from src.services.error_logging_service import get_error_logging_service
                from src.db.base import SessionLocal
                db = SessionLocal()
                try:
                    error_service = get_error_logging_service(db)
                    error_service.log_error(
                        error=e,
                        service_name="google_ads_service",
                        endpoint="create_search_campaign_with_ads",
                        user_id=user_id,
                        severity="error",
                        metadata={"customer_id": customer_id, "campaign_name": campaign_name}
                    )
                finally:
                    db.close()
            except Exception as log_error:
                logger.warning(f"Failed to log error to database: {str(log_error)}")
            
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def create_campaign_for_user(
        self,
        user_id: int,
        customer_id: str,
        campaign_name: str,
        campaign_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a Google Ads campaign for a specific user.
        Legacy method - use create_search_campaign_with_ads for Step 8-9 integration.
        
        Args:
            user_id: FinderOS user ID
            customer_id: Google Ads customer ID (format: XXX-XXX-XXXX)
            campaign_name: Name for the campaign
            campaign_config: Campaign configuration dictionary
        
        Returns:
            Dictionary with campaign creation result
        """
        # Delegate to new method if product_info and ad_data are provided
        if "product_info" in campaign_config and "ad_data" in campaign_config:
            return self.create_search_campaign_with_ads(
                customer_id=customer_id,
                user_id=user_id,
                campaign_name=campaign_name,
                product_info=campaign_config["product_info"],
                ad_data=campaign_config["ad_data"],
                budget_amount_micros=campaign_config.get("budget_amount_micros", 10000000),
                user_list_id=campaign_config.get("user_list_id")
            )
        
        # Fallback to basic implementation
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Ads service not available"
            }
        
        try:
            customer_service = self.get_customer_client(customer_id)
            if not customer_service:
                return {
                    "success": False,
                    "error": "Failed to get customer client"
                }
            
            logger.info(f"Campaign creation requested for user {user_id}, customer {customer_id}")
            
            return {
                "success": True,
                "message": "Campaign creation initiated",
                "user_id": user_id,
                "customer_id": customer_id,
                "campaign_name": campaign_name
            }
            
        except GoogleAdsException as e:
            logger.error(f"Google Ads API error: {str(e)}")
            return {
                "success": False,
                "error": f"Google Ads API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error creating campaign: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _hash_email(self, email: str) -> str:
        """
        Hash email address using SHA-256 for Customer Match.
        Email must be normalized (lowercase, trimmed) before hashing.
        
        Args:
            email: Email address to hash
        
        Returns:
            Base64-encoded SHA-256 hash
        """
        # Normalize email: lowercase and trim whitespace
        normalized_email = email.lower().strip()
        
        # Hash with SHA-256
        hash_object = hashlib.sha256(normalized_email.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        
        # Convert to base64 (Google Ads requires base64)
        hash_bytes = bytes.fromhex(hash_hex)
        hash_base64 = base64.b64encode(hash_bytes).decode('utf-8')
        
        return hash_base64
    
    def create_user_list(
        self,
        customer_id: str,
        list_name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Customer User List in Google Ads.
        
        Args:
            customer_id: Google Ads customer ID (format: XXX-XXX-XXXX, remove dashes)
            list_name: Name for the user list
            description: Optional description
        
        Returns:
            Dictionary with user list creation result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Ads service not available"
            }
        
        if not GOOGLE_ADS_AVAILABLE:
            return {
                "success": False,
                "error": "google-ads library not installed"
            }
        
        try:
            # Remove dashes from customer ID
            customer_id_clean = customer_id.replace("-", "")
            
            # Get services
            customer_service = self.client.get_service("CustomerUserListService")
            customer_operation = self.client.get_type("CustomerUserListOperation")
            
            # Create user list
            user_list = customer_operation.create
            user_list.name = list_name
            user_list.description = description or f"Customer Match list: {list_name}"
            user_list.membership_status = UserListMembershipStatusEnum.UserListMembershipStatus.OPEN
            user_list.membership_life_span = 365   # Days
            
            # Set membership type to CUSTOMER_MATCH
            user_list.type = UserListTypeEnum.UserListType.CUSTOMER_MATCH
            
            # Create operation
            operation = customer_operation
            operation.create.CopyFrom(user_list)
            
            # Execute mutation
            response = customer_service.mutate_customer_user_lists(
                customer_id=customer_id_clean,
                operations=[operation]
            )
            
            user_list_resource_name = response.results[0].resource_name
            user_list_id = user_list_resource_name.split("/")[-1]
            
            logger.info(f"User list created: {user_list_id} - {list_name}")
            
            return {
                "success": True,
                "user_list_id": user_list_id,
                "user_list_resource_name": user_list_resource_name,
                "list_name": list_name,
                "message": "User list created successfully"
            }
            
        except GoogleAdsException as e:
            error_messages = []
            for error in e.failure.errors:
                error_messages.append(f"{error.error_code.error_code}: {error.message}")
            logger.error(f"Google Ads API error creating user list: {'; '.join(error_messages)}")
            return {
                "success": False,
                "error": f"Google Ads API error: {'; '.join(error_messages)}"
            }
        except Exception as e:
            logger.error(f"Error creating user list: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def upload_customer_match_audience(
        self,
        customer_id: str,
        audience_name: str,
        email_list: List[str],
        description: Optional[str] = None,
        user_list_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload Customer Match audience using email addresses.
        Used for targeting specific personnel from Step 7 (Target Personnel).
        
        This function:
        1. Creates a User List if user_list_id is not provided
        2. Hashes email addresses (SHA-256, base64)
        3. Creates an OfflineUserDataJob
        4. Uploads hashed emails to the job
        5. Runs the job to add users to the list
        
        Args:
            customer_id: Google Ads customer ID (format: XXX-XXX-XXXX)
            audience_name: Name for the audience/user list
            email_list: List of email addresses to target (from Step 7 personas)
            description: Optional description for the audience
            user_list_id: Optional existing user list ID. If not provided, creates a new list
        
        Returns:
            Dictionary with upload result including user_list_id and job_id
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Ads service not available"
            }
        
        if not GOOGLE_ADS_AVAILABLE:
            return {
                "success": False,
                "error": "google-ads library not installed"
            }
        
        if not email_list:
            return {
                "success": False,
                "error": "Email list is empty"
            }
        
        try:
            # Remove dashes from customer ID
            customer_id_clean = customer_id.replace("-", "")
            
            # Step 1: Create user list if not provided
            if not user_list_id:
                list_result = self.create_user_list(
                    customer_id=customer_id,
                    list_name=audience_name,
                    description=description
                )
                
                if not list_result.get("success"):
                    return list_result
                
                user_list_id = list_result["user_list_id"]
                user_list_resource_name = list_result["user_list_resource_name"]
            else:
                user_list_resource_name = f"customers/{customer_id_clean}/customerUserLists/{user_list_id}"
            
            # Step 2: Hash email addresses
            logger.info(f"Hashing {len(email_list)} email addresses...")
            hashed_emails = []
            valid_emails = []
            
            for email in email_list:
                if email and "@" in email:   # Basic email validation
                    hashed_email = self._hash_email(email)
                    hashed_emails.append(hashed_email)
                    valid_emails.append(email)
            
            if not hashed_emails:
                return {
                    "success": False,
                    "error": "No valid email addresses found"
                }
            
            logger.info(f"Valid emails: {len(valid_emails)}/{len(email_list)}")
            
            # Step 3: Create OfflineUserDataJob
            offline_user_data_service = self.client.get_service("OfflineUserDataJobService")
            offline_user_data_job = self.client.get_type("OfflineUserDataJob")
            
            # Set job type to CUSTOMER_MATCH_USER_LIST
            offline_user_data_job.type = OfflineUserDataJobTypeEnum.OfflineUserDataJobType.CUSTOMER_MATCH_USER_LIST
            
            # Create operation
            operation = self.client.get_type("OfflineUserDataJobOperation")
            operation.create.CopyFrom(offline_user_data_job)
            
            # Create the job
            response = offline_user_data_service.create_offline_user_data_job(
                customer_id=customer_id_clean,
                job=offline_user_data_job
            )
            
            job_resource_name = response.resource_name
            job_id = job_resource_name.split("/")[-1]
            
            logger.info(f"OfflineUserDataJob created: {job_id}")
            
            # Step 4: Add user data to the job
            user_data_operation = self.client.get_type("OfflineUserDataJobOperation")
            
            # Create user identifiers
            user_identifiers = []
            for hashed_email in hashed_emails:
                user_identifier = self.client.get_type("UserIdentifier")
                user_identifier.hashed_email = hashed_email
                user_identifiers.append(user_identifier)
            
            # Create offline user data
            offline_user_data = self.client.get_type("OfflineUserData")
            offline_user_data.user_identifiers.extend(user_identifiers)
            offline_user_data.user_list.CopyFrom(
                self.client.get_type("UserList")
            )
            offline_user_data.user_list.customer_user_list = user_list_resource_name
            
            # Add to operation
            user_data_operation.create.user_data.CopyFrom(offline_user_data)
            
            # Add operations (batch in chunks of 1000)
            chunk_size = 1000
            for i in range(0, len(user_identifiers), chunk_size):
                chunk = user_identifiers[i:i + chunk_size]
                
                offline_user_data_chunk = self.client.get_type("OfflineUserData")
                offline_user_data_chunk.user_identifiers.extend(chunk)
                offline_user_data_chunk.user_list.CopyFrom(
                    self.client.get_type("UserList")
                )
                offline_user_data_chunk.user_list.customer_user_list = user_list_resource_name
                
                operation_chunk = self.client.get_type("OfflineUserDataJobOperation")
                operation_chunk.create.user_data.CopyFrom(offline_user_data_chunk)
                
                # Add user data to job
                offline_user_data_service.add_offline_user_data_job_operations(
                    resource_name=job_resource_name,
                    operations=[operation_chunk]
                )
            
            logger.info(f"Added {len(user_identifiers)} user identifiers to job {job_id}")
            
            # Step 5: Run the job
            offline_user_data_service.run_offline_user_data_job(
                resource_name=job_resource_name
            )
            
            logger.info(f"OfflineUserDataJob {job_id} started")
            
            return {
                "success": True,
                "message": "Customer Match audience upload initiated",
                "user_list_id": user_list_id,
                "user_list_resource_name": user_list_resource_name,
                "job_id": job_id,
                "job_resource_name": job_resource_name,
                "audience_name": audience_name,
                "email_count": len(valid_emails),
                "hashed_count": len(hashed_emails),
                "status": "processing"
            }
            
        except GoogleAdsException as e:
            error_messages = []
            for error in e.failure.errors:
                error_messages.append(f"{error.error_code.error_code}: {error.message}")
            logger.error(f"Google Ads API error uploading Customer Match: {'; '.join(error_messages)}")
            return {
                "success": False,
                "error": f"Google Ads API error: {'; '.join(error_messages)}"
            }
        except Exception as e:
            logger.error(f"Error uploading Customer Match audience: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def upload_personas_to_customer_match(
        self,
        customer_id: str,
        user_id: int,
        audience_name: str,
        persona_ids: Optional[List[int]] = None,
        db_session: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Upload personas from Step 7 (Target Personnel) to Google Ads Customer Match.
        This is a convenience function that retrieves personas from the database
        and uploads their email addresses to Google Ads.
        
        Args:
            customer_id: Google Ads customer ID
            user_id: FinderOS user ID (to filter personas)
            audience_name: Name for the audience/user list
            persona_ids: Optional list of specific persona IDs. If None, gets all personas for user
            db_session: Optional database session. If None, creates a new one
        
        Returns:
            Dictionary with upload result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Ads service not available"
            }
        
        try:
            # Import here to avoid circular dependencies
            from src.models.persona import Persona
            from src.db.base import SessionLocal
            
            # Get database session
            if db_session is None:
                db = SessionLocal()
                should_close = True
            else:
                db = db_session
                should_close = False
            
            try:
                # Query personas with email addresses
                query = db.query(Persona).filter(
                    Persona.user_id == user_id,
                    Persona.email.isnot(None),
                    Persona.email != ""
                )
                
                # Filter by specific persona IDs if provided
                if persona_ids:
                    query = query.filter(Persona.id.in_(persona_ids))
                
                personas = query.all()
                
                if not personas:
                    return {
                        "success": False,
                        "error": "No personas with email addresses found"
                    }
                
                # Extract email addresses
                email_list = [persona.email for persona in personas if persona.email]
                
                logger.info(f"Found {len(email_list)} personas with emails for user {user_id}")
                
                # Upload to Google Ads
                result = self.upload_customer_match_audience(
                    customer_id=customer_id,
                    audience_name=audience_name,
                    email_list=email_list,
                    description=f"Personas from FinderOS Step 7 (User ID: {user_id})"
                )
                
                # Add persona information to result
                if result.get("success"):
                    result["persona_count"] = len(personas)
                    result["persona_ids"] = [p.id for p in personas]
                
                return result
                
            finally:
                if should_close:
                    db.close()
                    
        except Exception as e:
            logger.error(f"Error uploading personas to Customer Match: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def create_dynamic_search_ad(
        self,
        customer_id: str,
        campaign_id: str,
        product_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create Dynamic Search Ad using product information from Step 1.
        
        Args:
            customer_id: Google Ads customer ID
            campaign_id: Campaign ID to attach the ad to
            product_info: Product information dictionary (name, description, category, etc.)
        
        Returns:
            Dictionary with ad creation result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Ads service not available"
            }
        
        try:
            # TODO: Implement Dynamic Search Ad creation
            # This will be implemented in subsequent steps
            
            logger.info(f"Dynamic Search Ad creation requested for product: {product_info.get('name', 'Unknown')}")
            
            return {
                "success": True,
                "message": "Dynamic Search Ad creation initiated",
                "product_name": product_info.get("name"),
                "campaign_id": campaign_id
            }
            
        except Exception as e:
            logger.error(f"Error creating Dynamic Search Ad: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def create_lead_form_extension(
        self,
        customer_id: str,
        campaign_id: str,
        form_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create Lead Form Extension for appointment scheduling (Step 11).
        Allows users to schedule appointments without leaving Google.
        
        Args:
            customer_id: Google Ads customer ID
            campaign_id: Campaign ID to attach the extension to
            form_config: Form configuration (fields, questions, etc.)
        
        Returns:
            Dictionary with extension creation result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Ads service not available"
            }
        
        try:
            # TODO: Implement Lead Form Extension creation
            # This will be implemented in subsequent steps
            
            logger.info(f"Lead Form Extension creation requested for campaign {campaign_id}")
            
            return {
                "success": True,
                "message": "Lead Form Extension creation initiated",
                "campaign_id": campaign_id
            }
            
        except Exception as e:
            logger.error(f"Error creating Lead Form Extension: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def get_campaign_performance(
        self,
        customer_id: str,
        campaign_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a Google Ads campaign.
        Returns impressions, clicks, cost, conversions, and other metrics.
        Used for Step 9 (Ad Display) dashboard.
        
        Args:
            customer_id: Google Ads customer ID (format: XXX-XXX-XXXX)
            campaign_id: Google Ads campaign ID
            start_date: Start date in YYYY-MM-DD format (default: 30 days ago)
            end_date: End date in YYYY-MM-DD format (default: today)
        
        Returns:
            Dictionary with campaign performance metrics
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Ads service not available"
            }
        
        if not GOOGLE_ADS_AVAILABLE:
            return {
                "success": False,
                "error": "google-ads library not installed"
            }
        
        try:
            from datetime import datetime, timedelta
            
            # Remove dashes from customer ID
            customer_id_clean = customer_id.replace("-", "")
            
            # Set default date range (last 30 days)
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Get GoogleAdsService
            google_ads_service = self.client.get_service("GoogleAdsService")
            
            # Build GAQL query
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_per_conversion,
                    metrics.all_conversions,
                    metrics.all_conversions_value,
                    campaign_budget.amount_micros,
                    campaign_budget.name
                FROM campaign
                WHERE campaign.id = {campaign_id}
                    AND segments.date >= '{start_date}'
                    AND segments.date <= '{end_date}'
            """
            
            # Execute query
            response = google_ads_service.search(customer_id=customer_id_clean, query=query)
            
            # Aggregate metrics across all rows
            total_impressions = 0
            total_clicks = 0
            total_cost_micros = 0
            total_conversions = 0
            total_conversions_value = 0
            total_all_conversions = 0
            total_all_conversions_value = 0
            campaign_name = ""
            campaign_status = ""
            budget_amount_micros = 0
            budget_name = ""
            
            rows_processed = 0
            for row in response:
                rows_processed += 1
                if not campaign_name:
                    campaign_name = row.campaign.name
                    campaign_status = row.campaign.status.name
                    budget_amount_micros = row.campaign_budget.amount_micros if row.campaign_budget else 0
                    budget_name = row.campaign_budget.name if row.campaign_budget else ""
                
                total_impressions += row.metrics.impressions
                total_clicks += row.metrics.clicks
                total_cost_micros += row.metrics.cost_micros
                total_conversions += row.metrics.conversions
                total_conversions_value += row.metrics.conversions_value
                total_all_conversions += row.metrics.all_conversions
                total_all_conversions_value += row.metrics.all_conversions_value
            
            # Calculate derived metrics
            cost_dollars = total_cost_micros / 1_000_000 if total_cost_micros > 0 else 0
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            avg_cpc = (total_cost_micros / total_clicks / 1_000_000) if total_clicks > 0 else 0
            cost_per_conversion = (total_cost_micros / total_conversions / 1_000_000) if total_conversions > 0 else 0
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            
            # Daily breakdown (if multiple rows)
            daily_metrics = []
            if rows_processed > 1:
                # Re-query for daily breakdown
                daily_query = f"""
                    SELECT
                        segments.date,
                        metrics.impressions,
                        metrics.clicks,
                        metrics.cost_micros,
                        metrics.conversions,
                        metrics.ctr
                    FROM campaign
                    WHERE campaign.id = {campaign_id}
                        AND segments.date >= '{start_date}'
                        AND segments.date <= '{end_date}'
                    ORDER BY segments.date
                """
                daily_response = google_ads_service.search(customer_id=customer_id_clean, query=daily_query)
                
                for row in daily_response:
                    daily_metrics.append({
                        "date": row.segments.date,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost": row.metrics.cost_micros / 1_000_000,
                        "conversions": row.metrics.conversions,
                        "ctr": row.metrics.ctr * 100 if row.metrics.ctr else 0
                    })
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "campaign_status": campaign_status,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "metrics": {
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "cost": cost_dollars,
                    "conversions": total_conversions,
                    "conversions_value": total_conversions_value,
                    "all_conversions": total_all_conversions,
                    "all_conversions_value": total_all_conversions_value,
                    "ctr": round(ctr, 2),
                    "average_cpc": round(avg_cpc, 2),
                    "cost_per_conversion": round(cost_per_conversion, 2),
                    "conversion_rate": round(conversion_rate, 2)
                },
                "budget": {
                    "amount_micros": budget_amount_micros,
                    "amount_dollars": budget_amount_micros / 1_000_000 if budget_amount_micros > 0 else 0,
                    "name": budget_name
                },
                "daily_breakdown": daily_metrics
            }
            
        except GoogleAdsException as e:
            error_messages = []
            for error in e.failure.errors:
                error_messages.append(f"{error.error_code.error_code}: {error.message}")
            logger.error(f"Google Ads API error getting performance: {'; '.join(error_messages)}")
            return {
                "success": False,
                "error": f"Google Ads API error: {'; '.join(error_messages)}"
            }
        except Exception as e:
            logger.error(f"Error getting campaign performance: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def get_campaign_status(
        self,
        customer_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """
        Get status of a Google Ads campaign.
        
        Args:
            customer_id: Google Ads customer ID
            campaign_id: Campaign ID to check
        
        Returns:
            Dictionary with campaign status
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Ads service not available"
            }
        
        try:
            # Use performance query to get status
            performance = self.get_campaign_performance(customer_id, campaign_id)
            if performance.get("success"):
                return {
                    "success": True,
                    "campaign_id": campaign_id,
                    "status": performance.get("campaign_status", "unknown"),
                    "campaign_name": performance.get("campaign_name", "")
                }
            else:
                return performance
            
        except Exception as e:
            logger.error(f"Error getting campaign status: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }


# Singleton instance
_google_ads_service = None


def get_google_ads_service() -> GoogleAdsService:
    """
    Get singleton instance of GoogleAdsService.
    """
    global _google_ads_service
    if _google_ads_service is None:
        _google_ads_service = GoogleAdsService()
    return _google_ads_service

