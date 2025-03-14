from fastapi import FastAPI, Depends, HTTPException, Request
# from starlette.middleware.sessions import SessionMiddleware
from constants import SECRET_KEY

from routers.product_router import product_router
from routers.supplier_router import supplier_router
from routers.user_router import app_user_router
from routers.recipe_router import recipe_router
from routers.health_router import health_router
from routers.auth_router import auth_router
from routers.business_router import business_router
from features.auth.decoder import verify_token
from fastapi.middleware.cors import CORSMiddleware
# from prometheus_fastapi_instrumentator import Instrumentator


# from prometheus_client import generate_latest, Counter, Histogram, Summary,REGISTRY
# from starlette.responses import Response


# Define Prometheus metrics as module-level singletons
# REQUEST_COUNT = Counter('request_count', 'Total number of requests', registry=REGISTRY)
# REQUEST_LATENCY = Histogram('request_latency_seconds', 'Latency of HTTP requests in seconds', registry=REGISTRY)
# REQUEST_SIZE = Summary('request_size_bytes', 'Size of HTTP requests in bytes', registry=REGISTRY)

# ----------- App initialisation -------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# # Enable Prometheus monitoring
# Instrumentator().instrument(app).expose(app, endpoint="/metrics")


app.include_router(auth_router)
app.include_router(supplier_router) # , dependencies=[Depends(verify_token)]
app.include_router(product_router) # , dependencies=[Depends(verify_token)]
app.include_router(recipe_router) # , dependencies=[Depends(verify_token)]
app.include_router(health_router) # , dependencies=[Depends(verify_token)]
app.include_router(app_user_router)
app.include_router(business_router)


# @app.middleware("http")
# async def add_metrics(request: Request, call_next):
#     with REQUEST_LATENCY.time():
#         response = await call_next(request)
#     REQUEST_COUNT.inc()
#     REQUEST_SIZE.observe(len(await request.body()))
#     return response

# @app.get("/metrics")
# async def metrics():
#     return Response(generate_latest(REGISTRY), media_type="text/plain")
# ------------- Standard endpoints -----------------------------------------------

@app.get("/")
def home():
    return {'data': 'Hello from the other side'}
