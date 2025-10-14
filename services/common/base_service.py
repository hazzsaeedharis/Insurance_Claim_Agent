"""
Base Service Class for Insurance Claim Agent microservices.
Provides standardized FastAPI setup, middleware, error handling, and common endpoints.
"""

import os
import sys
import time
from typing import Optional, Callable, Any, Dict
from functools import wraps
from datetime import datetime
import traceback

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.common.logger import get_logger, set_correlation_id
from services.common.metrics import increment, timer, gauge


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", None)
        if not correlation_id:
            import uuid
            correlation_id = str(uuid.uuid4())
        
        # Set correlation ID in context
        set_correlation_id(correlation_id)
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class BaseService:
    """Base class for all microservices with common functionality."""
    
    def __init__(
        self,
        service_name: str,
        version: str = "1.0.0",
        description: str = "",
        enable_cors: bool = True,
        enable_metrics: bool = True,
        enable_health_check: bool = True,
        enable_auth: bool = True,
        custom_middleware: Optional[list] = None
    ):
        """
        Initialize base service with FastAPI app and common middleware.
        
        Args:
            service_name: Name of the service
            version: API version
            description: Service description
            enable_cors: Enable CORS middleware
            enable_metrics: Enable metrics collection
            enable_health_check: Add health check endpoint
            enable_auth: Enable authentication middleware
            custom_middleware: Additional middleware to add
        """
        self.service_name = service_name
        self.version = version
        self.logger = get_logger(service_name)
        
        # Create FastAPI app
        self.app = FastAPI(
            title=f"{service_name} API",
            description=description or f"API for {service_name}",
            version=version,
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        
        # Add middleware
        self._add_middleware(enable_cors, enable_metrics, custom_middleware)
        
        # Add exception handlers
        self._add_exception_handlers()
        
        # Add common endpoints
        if enable_health_check:
            self._add_health_check()
        
        if enable_metrics:
            self._add_metrics_endpoint()
        
        # Log service initialization
        self.logger.info(f"{service_name} v{version} initialized")
    
    def _add_middleware(self, enable_cors: bool, enable_metrics: bool, custom_middleware: Optional[list]):
        """Add middleware to the FastAPI app."""
        # Correlation ID middleware
        self.app.add_middleware(CorrelationIdMiddleware)
        
        # CORS middleware
        if enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Request timing middleware
        if enable_metrics:
            @self.app.middleware("http")
            async def add_metrics(request: Request, call_next):
                start_time = time.perf_counter()
                
                # Track request
                increment(f"{self.service_name}.request.count", labels={
                    "method": request.method,
                    "path": request.url.path
                })
                
                # Process request
                try:
                    response = await call_next(request)
                    
                    # Track response
                    increment(f"{self.service_name}.response.count", labels={
                        "method": request.method,
                        "path": request.url.path,
                        "status": str(response.status_code)
                    })
                    
                    # Track timing
                    duration = time.perf_counter() - start_time
                    timer(f"{self.service_name}.request.duration", labels={
                        "method": request.method,
                        "path": request.url.path
                    }).__enter__()
                    
                    return response
                except Exception as e:
                    increment(f"{self.service_name}.error.count", labels={
                        "method": request.method,
                        "path": request.url.path,
                        "error": type(e).__name__
                    })
                    raise
        
        # Add custom middleware
        if custom_middleware:
            for middleware in custom_middleware:
                self.app.add_middleware(middleware)
    
    def _add_exception_handlers(self):
        """Add exception handlers for common error cases."""
        
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            """Handle validation errors."""
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Validation Error",
                    "detail": exc.errors(),
                    "body": exc.body,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        @self.app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            """Handle HTTP exceptions."""
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "status_code": exc.status_code,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Handle unexpected exceptions."""
            self.logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    def _add_health_check(self):
        """Add health check endpoint."""
        
        @self.app.get("/health", tags=["Health"])
        async def health_check():
            """
            Health check endpoint.
            
            Returns service status and basic information.
            """
            return {
                "status": "healthy",
                "service": self.service_name,
                "version": self.version,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _add_metrics_endpoint(self):
        """Add metrics endpoint."""
        from services.common.metrics import export_prometheus
        
        @self.app.get("/metrics", tags=["Monitoring"])
        async def metrics():
            """
            Prometheus metrics endpoint.
            
            Returns metrics in Prometheus format.
            """
            return Response(content=export_prometheus(), media_type="text/plain")
    
    def error_handler(self, func: Callable) -> Callable:
        """
        Decorator for consistent error handling in route handlers.
        
        Usage:
            @app.get("/example")
            @service.error_handler
            async def example_endpoint():
                # Your code here
                pass
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            except Exception as e:
                self.logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Internal error: {str(e)}" if os.getenv("DEBUG", "false").lower() == "true" else "Internal server error"
                )
        return wrapper
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """
        Run the service using uvicorn.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional uvicorn parameters
        """
        import uvicorn
        
        self.logger.info(f"Starting {self.service_name} on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, **kwargs)
    
    def add_api_route(self, *args, **kwargs):
        """Add route to the FastAPI app."""
        return self.app.add_api_route(*args, **kwargs)
    
    def include_router(self, *args, **kwargs):
        """Include a router in the FastAPI app."""
        return self.app.include_router(*args, **kwargs)
    
    def mount(self, *args, **kwargs):
        """Mount a sub-application."""
        return self.app.mount(*args, **kwargs)


# Example usage
if __name__ == "__main__":
    # Create a sample service
    service = BaseService(
        service_name="sample-service",
        version="1.0.0",
        description="Sample service using BaseService class"
    )
    
    # Add a custom endpoint
    @service.app.get("/sample")
    @service.error_handler
    async def sample_endpoint():
        return {"message": "Hello from sample service!"}
    
    # Run the service
    service.run(port=8000)

