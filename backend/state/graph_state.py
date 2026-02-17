"""GraphState definition for LangGraph workflow.

This module defines the state object that tracks workflow data across
all agent nodes in the Aegis-8645 self-healing DevOps agent.
"""

from typing import TypedDict, List


class GraphState(TypedDict):
    """State object for LangGraph workflow.
    
    This TypedDict defines the structure of state that flows through
    the agent workflow, tracking logs, errors, analysis, and NPU metrics.
    
    Attributes:
        logs: List of raw log entries read from log files
        detected_error: The identified error message (e.g., HTTP 500 error)
        root_cause: LLM-generated analysis of why the error occurred
        suggested_fix: LLM-generated code diff or configuration change
        npu_stats: Dictionary containing NPU performance metrics with keys:
                   - latency_ms: Inference latency in milliseconds (float)
                   - utilization_percent: NPU utilization percentage (float)
    """
    logs: List[str]
    detected_error: str
    root_cause: str
    suggested_fix: str
    npu_stats: dict
