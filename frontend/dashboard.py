"""Streamlit dashboard for Aegis-8645 DevOps Agent.

This module implements the real-time telemetry dashboard for monitoring
NPU metrics and viewing workflow results.
"""

import streamlit as st
import requests
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Page configuration
st.set_page_config(
    page_title="Aegis-8645 DevOps Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'workflow_results' not in st.session_state:
    st.session_state.workflow_results = None
if 'npu_history' not in st.session_state:
    st.session_state.npu_history = []
if 'last_execution_time' not in st.session_state:
    st.session_state.last_execution_time = None


def call_monitoring_api(log_path: str) -> Optional[Dict[str, Any]]:
    """Call FastAPI /start-monitoring endpoint.
    
    Args:
        log_path: Path to log file to monitor
        
    Returns:
        API response as dictionary, or None if request failed
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/start-monitoring",
            json={"log_path": log_path},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the backend is running on http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. The workflow is taking longer than expected.")
        return None
    except Exception as e:
        st.error(f"Error calling API: {str(e)}")
        return None


def display_metrics(npu_stats: Optional[Dict[str, float]]):
    """Display NPU metrics with gauges.
    
    Args:
        npu_stats: Dictionary with latency_ms and utilization_percent
    """
    if not npu_stats:
        st.info("No NPU metrics available yet. Run a monitoring workflow to see metrics.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="NPU Latency",
            value=f"{npu_stats.get('latency_ms', 0):.2f} ms",
            help="Time taken for NPU inference"
        )
    
    with col2:
        st.metric(
            label="NPU Utilization",
            value=f"{npu_stats.get('utilization_percent', 0):.1f}%",
            help="NPU hardware utilization percentage"
        )


def display_results(detected_error: Optional[str], root_cause: Optional[str], suggested_fix: Optional[str]):
    """Display workflow results in formatted panels.
    
    Args:
        detected_error: The detected error message
        root_cause: Root cause analysis
        suggested_fix: Generated code fix
    """
    if not detected_error:
        st.success("✅ No errors detected in the log file!")
        return
    
    # Detected Error
    with st.expander("🔴 Detected Error", expanded=True):
        st.code(detected_error, language="text")
    
    # Root Cause Analysis
    if root_cause:
        with st.expander("🔍 Root Cause Analysis", expanded=True):
            st.markdown(root_cause)
    
    # Suggested Fix
    if suggested_fix:
        with st.expander("🔧 Suggested Fix", expanded=True):
            st.code(suggested_fix, language="diff")


def render_dashboard():
    """Render main Streamlit dashboard."""
    
    # Header Section
    st.title("🛡️ Aegis-8645 DevOps Agent")
    st.markdown("**Self-Healing DevOps Agent with AMD Ryzen AI NPU**")
    
    # Check API health
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health_response.status_code == 200:
            st.sidebar.success("✅ Backend API: Connected")
        else:
            st.sidebar.error("❌ Backend API: Error")
    except:
        st.sidebar.error("❌ Backend API: Disconnected")
    
    # NPU Status
    st.sidebar.info("🔧 NPU Mode: Mock (Development)")
    
    st.sidebar.markdown("---")
    
    # Control Panel
    st.sidebar.header("Control Panel")
    
    log_path = st.sidebar.text_input(
        "Log File Path",
        value="examples/sample_error.log",
        help="Enter the path to the log file you want to monitor"
    )
    
    if st.sidebar.button("🚀 Start Monitoring", type="primary", use_container_width=True):
        if not log_path:
            st.sidebar.error("Please enter a log file path")
        else:
            with st.spinner("Executing workflow..."):
                start_time = time.time()
                results = call_monitoring_api(log_path)
                execution_time = time.time() - start_time
                
                if results:
                    st.session_state.workflow_results = results
                    st.session_state.last_execution_time = execution_time
                    
                    # Add to NPU history if stats available
                    if results.get('npu_stats'):
                        st.session_state.npu_history.append({
                            'timestamp': datetime.now(),
                            'latency_ms': results['npu_stats']['latency_ms'],
                            'utilization_percent': results['npu_stats']['utilization_percent']
                        })
                    
                    st.sidebar.success(f"✅ Completed in {execution_time:.2f}s")
                    st.rerun()
    
    # Clear Results Button
    if st.sidebar.button("🗑️ Clear Results", use_container_width=True):
        st.session_state.workflow_results = None
        st.session_state.npu_history = []
        st.session_state.last_execution_time = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Display last execution time
    if st.session_state.last_execution_time:
        st.sidebar.metric(
            "Last Execution Time",
            f"{st.session_state.last_execution_time:.2f}s"
        )
    
    # Main Content Area
    st.markdown("---")
    
    # Metrics Section
    st.header("📊 NPU Metrics")
    
    if st.session_state.workflow_results:
        npu_stats = st.session_state.workflow_results.get('npu_stats')
        display_metrics(npu_stats)
        
        # NPU Utilization History Chart
        if len(st.session_state.npu_history) > 1:
            st.subheader("NPU Utilization Over Time")
            
            import pandas as pd
            df = pd.DataFrame(st.session_state.npu_history)
            st.line_chart(df.set_index('timestamp')['utilization_percent'])
    else:
        display_metrics(None)
    
    st.markdown("---")
    
    # Results Section
    st.header("📋 Workflow Results")
    
    if st.session_state.workflow_results:
        results = st.session_state.workflow_results
        
        display_results(
            detected_error=results.get('detected_error'),
            root_cause=results.get('root_cause'),
            suggested_fix=results.get('suggested_fix')
        )
    else:
        st.info("No workflow results yet. Click 'Start Monitoring' to begin.")
    
    # Footer
    st.markdown("---")
    st.caption("Aegis-8645 DevOps Agent v1.0.0 | Powered by AMD Ryzen AI NPU")


if __name__ == "__main__":
    render_dashboard()
