from fastapi import APIRouter,Request
from authlib.integrations.starlette_client import OAuth
from constants import FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET, SECRET_KEY

auth_router = APIRouter()

# OAuth configuration
oauth = OAuth()

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    redirect_uri='http://localhost:8000/auth/google',  # Redirect URI for Google
    client_kwargs={'scope': 'openid profile email'}
)

oauth.register(
    name='facebook',
    client_id=FACEBOOK_CLIENT_ID,
    client_secret=FACEBOOK_CLIENT_SECRET,
    authorize_url='https://www.facebook.com/v6.0/dialog/oauth',
    access_token_url='https://graph.facebook.com/v6.0/oauth/access_token',
    redirect_uri='http://localhost:8000/auth/facebook',  # Redirect URI for Facebook
    client_kwargs={'scope': 'email'}
)

oauth.register(
    name='instagram',
    client_id=INSTAGRAM_CLIENT_ID,
    client_secret=INSTAGRAM_CLIENT_SECRET,
    authorize_url='https://api.instagram.com/oauth/authorize',
    access_token_url='https://api.instagram.com/oauth/access_token',
    redirect_uri='http://localhost:8000/auth/instagram',  # Redirect URI for Instagram
    client_kwargs={'scope': 'user_profile,user_media'}
)

@auth_router.route('/login/{provider}')
async def login(request: Request, provider: str):
    redirect_uri = f'http://localhost:8000/auth/{provider}'
    return await oauth[provider].authorize_redirect(request, redirect_uri)

@auth_router.route('/auth/{provider}')
async def auth(request: Request, provider: str):
    token = await oauth[provider].authorize_access_token(request)
    user = await oauth[provider].parse_id_token(request, token)
    request.session['user'] = dict(user)
    return {'token': token, 'user': user}



