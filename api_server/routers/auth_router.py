from fastapi import APIRouter, Request, Depends, HTTPException, status
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import RedirectResponse
from core.api_models import AuthData_API
from features.user.user_net import login_for_access_token
import os

auth_router = APIRouter()

# OAuth configuration
oauth = OAuth()

# Register OAuth providers securely
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    redirect_uri="http://localhost:8000/auth/google",
    client_kwargs={"scope": "openid profile email"},
)

oauth.register(
    name="facebook",
    client_id=os.getenv("FACEBOOK_CLIENT_ID"),
    client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
    authorize_url="https://www.facebook.com/v6.0/dialog/oauth",
    access_token_url="https://graph.facebook.com/v6.0/oauth/access_token",
    redirect_uri="http://localhost:8000/auth/facebook",
    client_kwargs={"scope": "email"},
)

oauth.register(
    name="instagram",
    client_id=os.getenv("INSTAGRAM_CLIENT_ID"),
    client_secret=os.getenv("INSTAGRAM_CLIENT_SECRET"),
    authorize_url="https://api.instagram.com/oauth/authorize",
    access_token_url="https://api.instagram.com/oauth/access_token",
    redirect_uri="http://localhost:8000/auth/instagram",
    client_kwargs={"scope": "user_profile,user_media"},
)

SUPPORTED_PROVIDERS = {"google", "facebook", "instagram"}


@auth_router.get("/login/{provider}")
async def login(provider: str, request: Request):
    """Redirects user to the OAuth provider's login page."""
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")

    try:
        redirect_uri = f"http://localhost:8000/auth/{provider}"
        return await oauth[provider].authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OAuth error: {str(e)}")


@auth_router.get("/auth/{provider}")
async def auth(provider: str, request: Request):
    """Handles the OAuth provider's callback and retrieves user info."""
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")

    try:
        token = await oauth[provider].authorize_access_token(request)
        user = await oauth[provider].parse_id_token(request, token)
        request.session["user"] = dict(user)
        return {"token": token, "user": user}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"OAuth authentication failed: {str(e)}")


@auth_router.post("/authentication/token")
async def login_user(user: AuthData_API):
    """Authenticates the user and returns an access token."""
    try:
        return await login_for_access_token(user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Couldn't log in: {str(e)}")
