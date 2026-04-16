# main.py (using config)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from config import settings
from constants import SECRET_KEY
from core.exception_handler import APIException
from core.api_models import API_Resolution

# Import routers (same as above)
from routers.app_routers.user_router import app_user_router
from routers.app_routers.auth_router import auth_router
from routers.health_routers.person_router import person_router

from routers.app_routers.notification_router import notification_router
from routers.business_routers.product_router import product_router
from routers.business_routers.supplier_router import supplier_router
from routers.business_routers.staff_router import staff_router
from routers.business_routers.business_router import business_router
from routers.business_routers.document_router import document_router
from routers.health_routers.recipe_router import recipe_router
from routers.health_routers.health_router import health_router
from routers.search_router import search_router

from routers.business_routers.order_router import order_router
from routers.business_routers.cart_router import cart_router
from routers.business_routers.delivery_router import delivery_router
from routers.business_routers.service_router import service_router
from routers.business_routers.financial_router import financial_router
from routers.business_routers.business_operation_router import business_operation_router




# ==================== Exception Handlers ====================

def setup_exception_handlers(app: FastAPI):
    """Configure global exception handlers"""
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle all exceptions globally"""
        
        # Handle known APIException
        if isinstance(exc, APIException):
            resolution = API_Resolution(
                status=exc.status,
                error_code=exc.code,
                message=str(exc.details) if exc.details else exc.message,
            )
            return JSONResponse(
                status_code=exc.status,
                content=resolution.dict(),
            )
        
        # Handle unexpected internal errors
        resolution = API_Resolution(
            status=500,
            error_code="INTERNAL_SERVER_ERROR",
            message=str(exc),
        )
        return JSONResponse(
            status_code=500,
            content=resolution.dict(),
        )
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception):
        """Handle 404 errors"""
        resolution = API_Resolution(
            status=404,
            error_code="NOT_FOUND",
            message=f"Endpoint {request.url.path} not found",
        )
        return JSONResponse(
            status_code=404,
            content=resolution.dict(),
        )
    
    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc: Exception):
        """Handle method not allowed errors"""
        resolution = API_Resolution(
            status=405,
            error_code="METHOD_NOT_ALLOWED",
            message=f"Method {request.method} not allowed for {request.url.path}",
        )
        return JSONResponse(
            status_code=405,
            content=resolution.dict(),
        )


# ==================== Middleware Setup ====================

def setup_middleware(app: FastAPI):
    """Configure all middleware"""
    
    # Session middleware (must be added first)
    app.add_middleware(
        SessionMiddleware,
        secret_key=SECRET_KEY,
        max_age=3600,
        same_site="lax",
        https_only=False
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Optional: Add custom middleware for request logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log incoming requests"""
        import time
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log request details (optional)
        print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response


# ==================== Router Setup ====================

def setup_routers(app: FastAPI):
    """Configure all API routers"""
    
    # Authentication and user routes
    app.include_router(auth_router, prefix="/api", tags=["authentication"])
    app.include_router(app_user_router, prefix="/api", tags=["users"])
    
    # Business routes
    app.include_router(business_router, prefix="/api", tags=["business"])
    app.include_router(product_router, prefix="/api", tags=["products"])
    app.include_router(supplier_router, prefix="/api", tags=["suppliers"])
    app.include_router(person_router, prefix="/api", tags=["people"])
    app.include_router(staff_router, prefix="/api", tags=["staff"])
    app.include_router(document_router, prefix="/api", tags=["documents"])
    

    # Attach all sub-routers
    app.include_router(order_router, prefix="/business", tags=["business-orders"])
    app.include_router(cart_router, prefix="/business", tags=["business-carts"])
    app.include_router(delivery_router, prefix="/business", tags=["business-deliveries"])
    app.include_router(service_router, prefix="/business", tags=["business-services"])
    app.include_router(financial_router, prefix="/business", tags=["business-finance"])
    app.include_router(business_operation_router, prefix="/business", tags=["business-operations"])


    # Health routes
    app.include_router(health_router, prefix="/api", tags=["health"])
    app.include_router(recipe_router, prefix="/api", tags=["recipes"])
    
    # Notification routes
    app.include_router(notification_router, prefix="/api", tags=["notifications"])
    
    # Search routes
    app.include_router(search_router, prefix="/api", tags=["search"])
    
    # Note: Add authentication dependencies when needed
    # app.include_router(supplier_router, prefix="/api", dependencies=[Depends(verify_token)])


# ==================== Root Endpoints ====================

def setup_root_endpoints(app: FastAPI):
    """Configure root endpoints"""
    
    @app.get("/api")
    async def home():
        """Root endpoint"""
        return {
            'data': 'Hello from the other side',
            'version': '1.0.0',
            'docs': '/api/docs',
            'redoc': '/api/redoc'
        }
    
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'API',
            'timestamp': '2024-01-01T00:00:00Z'  # You can use datetime.now()
        }
    
    @app.get("/api/ready")
    async def readiness_check():
        """Readiness check for orchestration"""
        return {
            'status': 'ready',
            'checks': {
                'database': 'connected',  # Add actual DB check
                'cache': 'connected',      # Add actual cache check
            }
        }


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Setup instrumentation
    if not settings.DEBUG:
        Instrumentator().instrument(app).expose(app)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup routers
    setup_routers(app)
    
    # Setup root endpoints
    setup_root_endpoints(app)
    
    return app


def setup_middleware(app: FastAPI):
    """Configure all middleware"""
    
    # Session middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=SECRET_KEY,
        max_age=settings.SESSION_MAX_AGE,
        same_site=settings.SESSION_SAME_SITE,
        https_only=settings.SESSION_HTTPS_ONLY
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )