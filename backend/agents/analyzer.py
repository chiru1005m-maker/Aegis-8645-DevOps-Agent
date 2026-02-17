"""Error analysis agent node.

This module implements the analyze_error node that uses NPU inference
to determine root causes of detected errors in the Aegis-8645 workflow.
"""

import logging
from backend.state.graph_state import GraphState
from backend.npu.engine import RyzenInferenceEngine

logger = logging.getLogger(__name__)


def analyze_error(state: GraphState) -> GraphState:
    """Analyze detected error to determine root cause.
    
    This node receives a GraphState with detected_error populated and
    uses NPU inference to analyze the error and determine its root cause.
    
    Args:
        state: GraphState with detected_error populated
        
    Returns:
        Updated GraphState with root_cause and npu_stats populated
    """
    detected_error = state.get('detected_error', '')
    
    if not detected_error:
        logger.warning("No detected_error in state, skipping analysis")
        state['root_cause'] = ""
        return state
    
    logger.info("Analyzing detected error...")
    
    try:
        # Construct analysis prompt
        prompt = construct_analysis_prompt(detected_error, state.get('logs', []))
        
        # Initialize inference engine (uses mock mode by default)
        engine = RyzenInferenceEngine(use_mock=True)
        
        # Run inference
        response, npu_stats = engine.run_inference(prompt)
        
        # Extract root cause from response
        root_cause = parse_analysis_response(response)
        
        # Update state
        state['root_cause'] = root_cause
        state['npu_stats'] = npu_stats
        
        logger.info(f"Root cause analysis completed: {root_cause[:100]}...")
        
        return state
        
    except TimeoutError as e:
        logger.error(f"NPU inference timeout: {e}")
        state['root_cause'] = "Unable to analyze error: NPU inference timed out"
        state['npu_stats'] = {'latency_ms': 0, 'utilization_percent': 0, 'error': True}
        return state
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        state['root_cause'] = f"Unable to analyze error: {str(e)}"
        state['npu_stats'] = {'latency_ms': 0, 'utilization_percent': 0, 'error': True}
        return state


def construct_analysis_prompt(detected_error: str, logs: list) -> str:
    """Construct LLM prompt for error analysis.
    
    Creates a detailed prompt that includes the error message and
    surrounding log context to help the LLM determine root cause.
    
    Args:
        detected_error: The detected error message with context
        logs: List of all log entries for additional context
        
    Returns:
        Formatted prompt string for the LLM
    """
    # Get additional context from logs (last 10 entries)
    recent_logs = logs[-10:] if len(logs) > 10 else logs
    log_context = "\n".join(recent_logs) if recent_logs else "No additional logs available"
    
    prompt = f"""You are a DevOps expert analyzing application errors.

Error detected:
{detected_error}

Recent log context:
{log_context}

Analyze the root cause of this error. Consider:
- Code logic issues
- Configuration problems
- Resource constraints
- Dependency failures
- Network issues
- Database connectivity

Provide a concise root cause analysis explaining why this error occurred and what underlying issue caused it."""
    
    return prompt


def parse_analysis_response(response: str) -> str:
    """Parse LLM response to extract root cause explanation.
    
    Extracts and formats the root cause analysis from the LLM response.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Formatted root cause explanation
    """
    # For now, return the response as-is
    # In a production system, you might want to parse structured output
    return response.strip()
