"""FastAPI application for Aegis-8645 DevOps Agent.

This module implements the REST API for triggering monitoring workflows
and retrieving results.
"""

import logging
import asyncio
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.models import MonitoringRequest, MonitoringResponse, NPUStats
from backend.agents.workflow import execute_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Aegis-8645 DevOps Agent",
    description="Self-Healing DevOps Agent with AMD Ryzen AI NPU",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    """Handle file access errors."""
    logger.error(f"File not found: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": f"Failed to read log file: {str(exc)}",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError):
    """Handle file permission errors."""
    logger.error(f"Permission denied: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": f"Permission denied accessing file: {str(exc)}",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(TimeoutError)
async def timeout_error_handler(request: Request, exc: TimeoutError):
    """Handle workflow timeout errors."""
    logger.error(f"Workflow timeout: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Workflow execution timed out (>30s). Please try again.",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": f"Internal server error: {str(exc)}",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Aegis-8645 DevOps Agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post(
    "/start-monitoring",
    response_model=MonitoringResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Workflow completed successfully",
            "model": MonitoringResponse
        },
        422: {
            "description": "Validation error - invalid request"
        },
        500: {
            "description": "Workflow execution error",
            "model": MonitoringResponse
        }
    }
)
async def start_monitoring(request: MonitoringRequest) -> MonitoringResponse:
    """Trigger agent workflow for log monitoring.
    
    This endpoint accepts a log file path, executes the complete agent
    workflow (monitor → analyze → generate fix), and returns the results.
    
    Args:
        request: MonitoringRequest containing log_path
        
    Returns:
        MonitoringResponse with workflow results
        
    Raises:
        HTTPException: If workflow execution fails
    """
    log_path = request.log_path
    logger.info(f"Received monitoring request for: {log_path}")
    
    # Validate log path exists
    if not Path(log_path).exists():
        logger.error(f"Log file not found: {log_path}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read log file: {log_path}"
        )
    
    try:
        # Execute workflow with timeout (30 seconds)
        final_state = await asyncio.wait_for(
            asyncio.to_thread(execute_workflow, log_path),
            timeout=30.0
        )
        
        # Extract results from state
        detected_error = final_state.get('detected_error', '')
        root_cause = final_state.get('root_cause', '')
        suggested_fix = final_state.get('suggested_fix', '')
        npu_stats_dict = final_state.get('npu_stats', {})
        
        # Build NPU stats if available
        npu_stats = None
        if npu_stats_dict and 'latency_ms' in npu_stats_dict:
            npu_stats = NPUStats(
                latency_ms=npu_stats_dict['latency_ms'],
                utilization_percent=npu_stats_dict.get('utilization_percent', 0)
            )
        
        # Build response
        response = MonitoringResponse(
            status="completed",
            detected_error=detected_error if detected_error else None,
            root_cause=root_cause if root_cause else None,
            suggested_fix=suggested_fix if suggested_fix else None,
            npu_stats=npu_stats,
            message=None
        )
        
        logger.info("Workflow completed successfully")
        return response
        
    except asyncio.TimeoutError:
        logger.error(f"Workflow timeout after 30 seconds for: {log_path}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Workflow execution timed out (>30s). Please try again."
        )
    
    except FileNotFoundError as e:
        logger.error(f"File access error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read log file: {log_path}"
        )
    
    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Permission denied accessing file: {log_path}"
        )
    
    except Exception as e:
        logger.error(f"Workflow execution error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
