# services/oauth_config_service.py
from authlib.integrations.starlette_client import OAuth
from constants import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
import os

class OAuthConfigService:
    """Service for OAuth provider configuration"""
    
    SUPPORTED_PROVIDERS = {"google", "facebook", "instagram"}
    
    def __init__(self):
        self.oauth = OAuth()
        self._configure_providers()
    
    def _configure_providers(self):
        """Configure all OAuth providers."""
        
        # Google OAuth
        self.oauth.register(
            name="google",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid email profile"
            },
        )
        
        # Facebook OAuth
        self.oauth.register(
            name="facebook",
            client_id=os.getenv("FACEBOOK_CLIENT_ID"),
            client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
            authorize_url="https://www.facebook.com/v18.0/dialog/oauth",
            access_token_url="https://graph.facebook.com/v18.0/oauth/access_token",
            api_base_url="https://graph.facebook.com/v18.0/",
            client_kwargs={"scope": "email public_profile"},
        )
        
        # Instagram OAuth
        self.oauth.register(
            name="instagram",
            client_id=os.getenv("INSTAGRAM_CLIENT_ID"),
            client_secret=os.getenv("INSTAGRAM_CLIENT_SECRET"),
            authorize_url="https://api.instagram.com/oauth/authorize",
            access_token_url="https://api.instagram.com/oauth/access_token",
            client_kwargs={"scope": "user_profile user_media"},
        )
    
    def get_client(self, provider: str):
        """Get OAuth client for provider."""
        if provider not in self.SUPPORTED_PROVIDERS:
            return None
        return getattr(self.oauth, provider)
    
    def is_supported_provider(self, provider: str) -> bool:
        """Check if provider is supported."""
        return provider in self.SUPPORTED_PROVIDERS