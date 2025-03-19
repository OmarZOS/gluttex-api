
import os


SECRET_KEY = os.getenv("API_SECRET_KEY",'')
ALGORITHM = os.getenv("API_ALGORITHM",'')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",10))
AUTH_DATABASE_URL = os.getenv("AUTH_DATABASE_URL",'')

# specify the allowed origins to access the auth provider
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS",'*').split(',')
