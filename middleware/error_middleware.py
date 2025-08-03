from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from exceptions import PlaicubeException, ValidationException, PipelineException, ServiceException
from utils.logger import logger

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except ValidationException as e:
            logger.error(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation Error",
                    "message": str(e),
                    "type": "validation_error"
                }
            )
            
        except PipelineException as e:
            logger.error(f"Pipeline error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Pipeline Error",
                    "message": str(e),
                    "type": "pipeline_error"
                }
            )
            
        except ServiceException as e:
            logger.error(f"Service error: {str(e)}")
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service Error",
                    "message": str(e),
                    "type": "service_error"
                }
            )
            
        except PlaicubeException as e:
            logger.error(f"Plaicube error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Error",
                    "message": str(e),
                    "type": "internal_error"
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "type": "unexpected_error"
                }
            ) 