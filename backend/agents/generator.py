"""Fix generation agent node.

This module implements the generate_fix node that uses NPU inference
to create code fixes or configuration changes for detected errors.
"""

import logging
from backend.state.graph_state import GraphState
from backend.npu.engine import RyzenInferenceEngine

logger = logging.getLogger(__name__)


def generate_fix(state: GraphState) -> GraphState:
    """Generate fix suggestion based on root cause analysis.
    
    This node receives a GraphState with root_cause populated and uses
    NPU inference to generate a code fix or configuration change.
    
    Args:
        state: GraphState with root_cause populated
        
    Returns:
        Updated GraphState with suggested_fix and npu_stats populated
    """
    root_cause = state.get('root_cause', '')
    detected_error = state.get('detected_error', '')
    
    if not root_cause:
        logger.warning("No root_cause in state, skipping fix generation")
        state['suggested_fix'] = ""
        return state
    
    logger.info("Generating fix suggestion...")
    
    try:
        # Construct fix generation prompt
        prompt = construct_fix_prompt(detected_error, root_cause)
        
        # Initialize inference engine (uses mock mode by default)
        engine = RyzenInferenceEngine(use_mock=True)
        
        # Run inference
        response, npu_stats = engine.run_inference(prompt)
        
        # Parse and format the fix
        suggested_fix = parse_fix_response(response)
        
        # Update state
        state['suggested_fix'] = suggested_fix
        
        # Update NPU stats (accumulate with previous stats if available)
        existing_stats = state.get('npu_stats', {})
        if existing_stats and not existing_stats.get('error'):
            # Average the stats from both inference calls
            state['npu_stats'] = {
                'latency_ms': (existing_stats.get('latency_ms', 0) + npu_stats['latency_ms']) / 2,
                'utilization_percent': (existing_stats.get('utilization_percent', 0) + npu_stats['utilization_percent']) / 2
            }
        else:
            state['npu_stats'] = npu_stats
        
        logger.info(f"Fix generation completed: {len(suggested_fix)} characters")
        
        return state
        
    except TimeoutError as e:
        logger.error(f"NPU inference timeout: {e}")
        state['suggested_fix'] = "Unable to generate fix: NPU inference timed out"
        return state
    except Exception as e:
        logger.error(f"Error during fix generation: {e}", exc_info=True)
        state['suggested_fix'] = f"Unable to generate fix: {str(e)}"
        return state


def construct_fix_prompt(detected_error: str, root_cause: str) -> str:
    """Construct LLM prompt for fix generation.
    
    Creates a detailed prompt that includes the error, root cause analysis,
    and instructions for generating a code fix in unified diff format.
    
    Args:
        detected_error: The detected error message
        root_cause: The root cause analysis from previous node
        
    Returns:
        Formatted prompt string for the LLM
    """
    prompt = f"""You are a DevOps expert generating fixes for application errors.

Error: {detected_error}

Root Cause: {root_cause}

Generate a fix for this issue. Provide:
- File path to modify
- Unified diff format showing changes
- Explanatory comments in the code

Format your response as a unified diff that can be applied directly.
Use the standard diff format with:
--- a/path/to/file
+++ b/path/to/file
@@ line_numbers @@
 context lines
-removed lines
+added lines

Be specific and include only the necessary changes to fix the issue."""
    
    return prompt


def parse_fix_response(response: str) -> str:
    """Parse LLM response to extract code fix.
    
    Extracts and formats the code fix from the LLM response, ensuring
    it follows unified diff format with file paths and line numbers.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Formatted code fix in unified diff format
    """
    # Clean up the response
    fix = response.strip()
    
    # Validate that it contains diff markers
    if not any(marker in fix for marker in ['---', '+++', '@@']):
        logger.warning("Response doesn't contain unified diff markers, wrapping it")
        # Wrap in basic diff format if not present
        fix = f"""--- a/application/code.py
+++ b/application/code.py
@@ -1,1 +1,1 @@
{fix}"""
    
    return fix
