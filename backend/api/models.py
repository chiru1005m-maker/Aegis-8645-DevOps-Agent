"""Pydantic models for FastAPI endpoints.

This module defines request and response models for the Aegis-8645 API.
"""

from typing import Optional
from pydantic import BaseModel, Field


class MonitoringRequest(BaseModel):
    """Request model for /start-monitoring endpoint.
    
    Attributes:
        log_path: Path to the log file to monitor
    """
    log_path: str = Field(
        ...,
        description="Path to the log file to monitor",
        example="/var/log/application.log"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "log_path": "/var/log/application.log"
            }
        }


class NPUStats(BaseModel):
    """NPU performance metrics.
    
    Attributes:
        latency_ms: Inference latency in milliseconds
        utilization_percent: NPU utilization percentage
    """
    latency_ms: float = Field(
        ...,
        description="Inference latency in milliseconds",
        ge=0
    )
    utilization_percent: float = Field(
        ...,
        description="NPU utilization percentage",
        ge=0,
        le=100
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "latency_ms": 245.3,
                "utilization_percent": 67.5
            }
        }


class MonitoringResponse(BaseModel):
    """Response model for /start-monitoring endpoint.
    
    Attributes:
        status: Workflow execution status ("completed" or "error")
        detected_error: The detected error message (if any)
        root_cause: Root cause analysis from LLM (if error detected)
        suggested_fix: Generated code fix (if error detected)
        npu_stats: NPU performance metrics (if inference ran)
        message: Error message (if status is "error")
    """
    status: str = Field(
        ...,
        description="Workflow execution status",
        pattern="^(completed|error)$"
    )
    detected_error: Optional[str] = Field(
        None,
        description="The detected error message"
    )
    root_cause: Optional[str] = Field(
        None,
        description="Root cause analysis from LLM"
    )
    suggested_fix: Optional[str] = Field(
        None,
        description="Generated code fix in unified diff format"
    )
    npu_stats: Optional[NPUStats] = Field(
        None,
        description="NPU performance metrics"
    )
    message: Optional[str] = Field(
        None,
        description="Error message if status is 'error'"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "detected_error": "HTTP 500 Internal Server Error at /api/users",
                "root_cause": "NullPointerException due to missing user validation",
                "suggested_fix": "--- a/api/users.py\n+++ b/api/users.py\n@@ -10,6 +10,8 @@\n def get_user(user_id):\n+    if user_id is None:\n+        raise ValueError('user_id required')\n     return db.query(user_id)",
                "npu_stats": {
                    "latency_ms": 245.3,
                    "utilization_percent": 67.5
                }
            }
        }
