"""LangGraph workflow definition for Aegis-8645.

This module defines the agent workflow that orchestrates log monitoring,
error analysis, and fix generation using LangGraph's StateGraph.
"""

import logging
from typing import Literal
from langgraph.graph import StateGraph, END

from backend.state.graph_state import GraphState
from backend.agents.monitor import monitor_logs
from backend.agents.analyzer import analyze_error
from backend.agents.generator import generate_fix

logger = logging.getLogger(__name__)


def create_workflow() -> StateGraph:
    """Create LangGraph workflow with nodes and edges.
    
    Defines the complete agent workflow:
    1. monitor_logs: Entry point, reads logs and detects errors
    2. analyze_error: Analyzes detected errors (conditional)
    3. generate_fix: Generates code fixes
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize workflow with GraphState
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("monitor_logs", monitor_logs)
    workflow.add_node("analyze_error", analyze_error)
    workflow.add_node("generate_fix", generate_fix)
    
    # Set entry point
    workflow.set_entry_point("monitor_logs")
    
    # Add conditional edge from monitor_logs
    # If error detected, go to analyze_error; otherwise end
    workflow.add_conditional_edges(
        "monitor_logs",
        should_analyze_error,
        {
            "analyze": "analyze_error",
            "end": END
        }
    )
    
    # Add edge from analyze_error to generate_fix
    workflow.add_edge("analyze_error", "generate_fix")
    
    # Add edge from generate_fix to END
    workflow.add_edge("generate_fix", END)
    
    # Compile workflow
    app = workflow.compile()
    
    logger.info("LangGraph workflow compiled successfully")
    return app


def should_analyze_error(state: GraphState) -> Literal["analyze", "end"]:
    """Determine if error analysis should proceed.
    
    Conditional routing function that checks if an error was detected.
    
    Args:
        state: Current GraphState
        
    Returns:
        "analyze" if error detected, "end" otherwise
    """
    detected_error = state.get('detected_error', '')
    
    if detected_error:
        logger.info("Error detected, proceeding to analysis")
        return "analyze"
    else:
        logger.info("No error detected, ending workflow")
        return "end"


def execute_workflow(log_path: str) -> GraphState:
    """Execute complete workflow for given log file.
    
    Convenience function that initializes state, creates workflow,
    and executes it to completion.
    
    Args:
        log_path: Path to log file to monitor
        
    Returns:
        Final GraphState with all results
    """
    logger.info(f"Starting workflow execution for: {log_path}")
    
    try:
        # Initialize GraphState with empty values
        initial_state: GraphState = {
            'logs': [],
            'detected_error': '',
            'root_cause': '',
            'suggested_fix': '',
            'npu_stats': {},
            'log_path': log_path  # Add log_path to state
        }
        
        # Create and compile workflow
        app = create_workflow()
        
        # Execute workflow
        final_state = app.invoke(initial_state)
        
        logger.info("Workflow execution completed successfully")
        return final_state
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise
