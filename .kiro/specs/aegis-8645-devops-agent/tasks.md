# Implementation Plan: Aegis-8645 DevOps Agent

## Overview

This implementation plan breaks down the Aegis-8645 Self-Healing DevOps Agent into incremental coding tasks. The system will be built using Python with FastAPI for the backend, LangGraph for agent orchestration, and Streamlit for the frontend dashboard. We'll start with project structure, implement core NPU integration (with mock mode), build the LangGraph workflow, create the API layer, and finally add the telemetry dashboard.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure: backend/, frontend/, npu_core/
  - Create subdirectories: backend/api/, backend/agents/, backend/npu/, backend/state/
  - Create requirements.txt with dependencies: fastapi, uvicorn, langgraph, streamlit, onnxruntime, pydantic, hypothesis, pytest
  - Create __init__.py files in all Python package directories
  - Create .env.example for configuration
  - _Requirements: 1.1, 1.2, 1.5_

- [x] 2. Implement GraphState and state management
  - [x] 2.1 Create GraphState TypedDict in backend/state/graph_state.py
    - Define GraphState with typed fields: logs (List[str]), detected_error (str), root_cause (str), suggested_fix (str), npu_stats (dict)
    - Add type hints and docstrings
    - _Requirements: 2.1, 2.4, 2.5, 2.6, 2.7, 2.8_
  
  - [ ]* 2.2 Write property test for GraphState field types
    - **Property 3: GraphState Field Type Consistency**
    - **Validates: Requirements 2.4, 2.5, 2.6, 2.7, 2.8**
    - Use Hypothesis to generate random GraphState instances
    - Verify all fields have correct types
    - Verify npu_stats contains required keys

- [x] 3. Implement RyzenInferenceEngine with mock mode
  - [x] 3.1 Create RyzenInferenceEngine class in backend/npu/engine.py
    - Implement __init__ with model_path and use_mock parameters
    - Implement is_npu_available() method to detect AMD Ryzen AI hardware
    - Implement load_model() method (mock implementation initially)
    - Add logging for mock mode detection
    - _Requirements: 3.1, 3.2, 10.1, 10.7_
  
  - [x] 3.2 Implement run_inference() method with mock mode
    - Accept prompt string parameter
    - Return tuple of (response_text, npu_stats)
    - In mock mode: simulate latency (100-500ms), return mock responses
    - Track and return latency_ms and utilization_percent in npu_stats
    - Generate plausible mock responses based on prompt keywords
    - _Requirements: 3.2, 3.4, 3.5, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 3.3 Write property tests for NPU inference metrics
    - **Property 4: NPU Inference Returns Valid Metrics**
    - **Validates: Requirements 3.4, 3.5**
    - Test that npu_stats contains valid latency_ms (positive float)
    - Test that utilization_percent is between 0 and 100
  
  - [ ]* 3.4 Write property tests for mock mode bounds
    - **Property 19: Mock Mode Latency Within Bounds**
    - **Validates: Requirements 10.2**
    - **Property 20: Mock Mode Utilization Within Bounds**
    - **Validates: Requirements 10.3**
    - **Property 21: Mock Mode Returns Non-Empty Responses**
    - **Validates: Requirements 10.4, 10.5**
  
  - [ ]* 3.5 Write unit tests for RyzenInferenceEngine
    - Test mock mode detection
    - Test interface consistency between mock and real modes
    - Test error handling for invalid prompts

- [x] 4. Implement log monitoring node
  - [x] 4.1 Create monitor_logs function in backend/agents/monitor.py
    - Accept GraphState parameter with log_path in metadata
    - Read log file from specified path
    - Parse log entries (support plain text and JSON formats)
    - Detect error patterns: HTTP 500, exceptions, ERROR level logs
    - Extract error message with surrounding context
    - Update GraphState.logs and GraphState.detected_error
    - Return updated GraphState
    - _Requirements: 4.1, 4.4, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_
  
  - [ ]* 4.2 Write property tests for log parsing
    - **Property 5: Log Parsing Completeness**
    - **Validates: Requirements 7.1, 7.2**
    - **Property 6: Error Pattern Detection**
    - **Validates: Requirements 7.3, 7.4, 7.5, 7.6**
    - **Property 7: Error Detection Format Support**
    - **Validates: Requirements 7.7**
    - Generate random log files with various formats
    - Test that all lines are parsed correctly
    - Test that errors are detected across different patterns
  
  - [ ]* 4.3 Write unit tests for monitor_logs
    - Test with empty log file
    - Test with log file containing no errors
    - Test with various error patterns
    - Test error handling for missing files

- [x] 5. Implement error analysis node
  - [x] 5.1 Create analyze_error function in backend/agents/analyzer.py
    - Accept GraphState parameter with detected_error populated
    - Construct LLM prompt including error message and log context
    - Initialize RyzenInferenceEngine
    - Call run_inference() with constructed prompt
    - Parse LLM response to extract root cause
    - Update GraphState.root_cause and GraphState.npu_stats
    - Return updated GraphState
    - _Requirements: 4.2, 4.6, 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 5.2 Write property tests for error analysis
    - **Property 9: Analysis Node Populates Root Cause**
    - **Validates: Requirements 4.6, 8.4, 8.5**
    - **Property 13: Analyzer Prompt Contains Error Context**
    - **Validates: Requirements 8.1, 8.2, 8.3**
    - Test that root_cause is populated after execution
    - Test that prompts contain error and context
  
  - [ ]* 5.3 Write unit tests for analyze_error
    - Test with various error types
    - Test prompt construction
    - Test NPU stats update

- [x] 6. Implement fix generation node
  - [x] 6.1 Create generate_fix function in backend/agents/generator.py
    - Accept GraphState parameter with root_cause populated
    - Construct LLM prompt including root cause and error context
    - Call RyzenInferenceEngine.run_inference() with prompt
    - Parse LLM response to extract code diff
    - Format fix as unified diff with file paths and line numbers
    - Update GraphState.suggested_fix and GraphState.npu_stats
    - Return updated GraphState
    - _Requirements: 4.3, 4.8, 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 6.2 Write property tests for fix generation
    - **Property 10: Fix Generation Node Populates Suggested Fix**
    - **Validates: Requirements 4.8**
    - **Property 14: Fix Generator Prompt Contains Root Cause**
    - **Validates: Requirements 9.1, 9.2, 9.3**
    - **Property 15: Generated Fix Follows Unified Diff Format**
    - **Validates: Requirements 9.4, 9.5**
    - Test that suggested_fix is populated
    - Test that prompts contain root cause
    - Test that fixes follow unified diff format
  
  - [ ]* 6.3 Write unit tests for generate_fix
    - Test with various root causes
    - Test diff format validation
    - Test NPU stats update

- [x] 7. Checkpoint - Ensure all node tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement LangGraph workflow
  - [x] 8.1 Create workflow definition in backend/agents/workflow.py
    - Import StateGraph from langgraph
    - Define create_workflow() function
    - Add nodes: monitor_logs, analyze_error, generate_fix
    - Set entry point to monitor_logs
    - Add conditional edge from monitor_logs (check if error detected)
    - Add edge from analyze_error to generate_fix
    - Add edge from generate_fix to END
    - Compile and return workflow
    - _Requirements: 4.1, 4.2, 4.3, 4.5, 4.7, 4.10_
  
  - [x] 8.2 Create execute_workflow() function
    - Accept log_path parameter
    - Initialize GraphState with empty values and log_path in metadata
    - Invoke compiled workflow with initial state
    - Return final GraphState
    - Add error handling for workflow exceptions
    - _Requirements: 4.5, 4.7_
  
  - [ ]* 8.3 Write property tests for workflow execution
    - **Property 1: Agent Node State Passing**
    - **Validates: Requirements 2.2**
    - **Property 2: Agent Node State Modification**
    - **Validates: Requirements 2.3**
    - **Property 8: Workflow Routing on Error Detection**
    - **Validates: Requirements 4.5, 7.8**
    - **Property 11: Workflow Sequential Execution**
    - **Validates: Requirements 4.7**
    - **Property 12: NPU Stats Updated After Inference**
    - **Validates: Requirements 4.9**
    - **Property 22: Workflow Execution Completes**
    - **Validates: Requirements 5.5**
  
  - [ ]* 8.4 Write integration tests for complete workflow
    - Test end-to-end execution with sample log files
    - Test workflow with errors detected
    - Test workflow with no errors detected
    - Test state transitions between nodes

- [x] 9. Implement FastAPI backend
  - [x] 9.1 Create Pydantic models in backend/api/models.py
    - Define MonitoringRequest with log_path field
    - Define NPUStats with latency_ms and utilization_percent fields
    - Define MonitoringResponse with status, detected_error, root_cause, suggested_fix, npu_stats, message fields
    - Add validation and examples
    - _Requirements: 5.3_
  
  - [x] 9.2 Create FastAPI application in backend/api/main.py
    - Initialize FastAPI app
    - Import workflow execution function
    - Implement POST /start-monitoring endpoint
    - Accept MonitoringRequest, validate log_path
    - Execute workflow with provided log_path
    - Return MonitoringResponse with workflow results
    - Return HTTP 200 on success, HTTP 500 on error
    - Add error handling for file access and workflow errors
    - _Requirements: 5.1, 5.2, 5.4, 5.5, 5.6, 5.7, 5.8_
  
  - [ ]* 9.3 Write property tests for API responses
    - **Property 16: API Response Contains All Required Fields**
    - **Validates: Requirements 5.6**
    - **Property 17: API Returns Success Status on Completion**
    - **Validates: Requirements 5.7**
  
  - [ ]* 9.4 Write unit tests for FastAPI endpoints
    - Test /start-monitoring with valid log path
    - Test /start-monitoring with invalid log path
    - Test request validation errors (HTTP 422)
    - Test workflow error handling (HTTP 500)
    - Use FastAPI TestClient for testing

- [x] 10. Checkpoint - Ensure backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement Streamlit dashboard
  - [x] 11.1 Create dashboard layout in frontend/dashboard.py
    - Import streamlit and requests
    - Create header section with title and NPU status indicator
    - Create control panel with log path input and "Start Monitoring" button
    - Create metrics display section with placeholders for latency and utilization
    - Create results panel with expandable sections for error, root cause, and fix
    - Add session state management for storing workflow results
    - _Requirements: 6.1, 6.9_
  
  - [x] 11.2 Implement API integration and data display
    - Create call_monitoring_api() function to POST to /start-monitoring
    - Implement display_metrics() function to render NPU latency and utilization gauges
    - Implement display_results() function to render detected error, root cause, and suggested fix
    - Add line chart for NPU utilization over time (store history in session state)
    - Handle API errors and display error messages
    - Add loading indicators during workflow execution
    - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6, 6.8_
  
  - [ ]* 11.3 Write property tests for dashboard rendering
    - **Property 18: Dashboard Renders Complete Workflow Data**
    - **Validates: Requirements 6.2, 6.3, 6.4, 6.5, 6.6**
    - Test that all workflow data elements are included in rendered output
    - Use Streamlit testing utilities or mock rendering

- [x] 12. Create sample log files and configuration
  - [x] 12.1 Create sample log files in examples/ directory
    - Create sample_error.log with HTTP 500 errors
    - Create sample_exception.log with Python stack traces
    - Create sample_clean.log with no errors
    - Create sample_json.log with JSON-formatted logs
    - _Requirements: 7.7_
  
  - [x] 12.2 Create configuration and documentation files
    - Create config.py for application settings (NPU model path, API host/port)
    - Create README.md with setup instructions and usage examples
    - Create .env.example with environment variable templates
    - Document mock mode vs real NPU mode

- [x] 13. Add comprehensive error handling
  - [x] 13.1 Implement error handlers in backend/api/main.py
    - Add exception handler for file access errors
    - Add exception handler for workflow execution errors
    - Add exception handler for NPU inference errors
    - Add timeout handling for long-running inference (30s timeout)
    - Log all errors with timestamps and stack traces
    - _Requirements: Error Handling section_
  
  - [x] 13.2 Add error handling in workflow nodes
    - Add try-catch blocks in monitor_logs for file I/O errors
    - Add try-catch blocks in analyze_error for NPU errors with fallback
    - Add try-catch blocks in generate_fix for NPU errors with fallback
    - Add GraphState validation before each node execution
    - Log errors and continue with fallback values where appropriate

- [ ] 14. Final integration and testing
  - [ ] 14.1 Create end-to-end test script
    - Create test_e2e.py that starts FastAPI server
    - Test complete workflow with sample log files
    - Verify API responses contain all expected fields
    - Verify workflow executes in reasonable time (<5s in mock mode)
    - Test error scenarios (missing files, invalid formats)
  
  - [ ]* 14.2 Run all property tests with full iterations
    - Execute all property tests with 100+ iterations
    - Verify all 22 properties pass consistently
    - Generate coverage report (target: 85%+ overall)
  
  - [ ] 14.3 Create startup scripts
    - Create start_backend.sh to run FastAPI server (uvicorn backend.api.main:app)
    - Create start_frontend.sh to run Streamlit dashboard (streamlit run frontend/dashboard.py)
    - Create start_all.sh to run both backend and frontend
    - Add instructions to README.md

- [ ] 15. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The implementation uses Python with FastAPI, LangGraph, and Streamlit
- Mock NPU mode is implemented first; real NPU integration can be added later
- Property tests use Hypothesis with minimum 100 iterations for thorough validation
- Checkpoints ensure incremental validation throughout development
