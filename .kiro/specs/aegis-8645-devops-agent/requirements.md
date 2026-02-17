# Requirements Document

## Introduction

Aegis-8645 is a Self-Healing DevOps Agent that monitors application logs, detects errors, analyzes root causes, and suggests fixes using local LLM inference on AMD Ryzen AI NPU hardware. The system uses LangGraph for stateful multi-agent orchestration, FastAPI for the backend API, and Streamlit for real-time hardware telemetry visualization.

## Glossary

- **Aegis_System**: The complete self-healing DevOps agent system
- **NPU**: Neural Processing Unit - AMD Ryzen AI hardware accelerator for LLM inference
- **LangGraph**: Stateful multi-agent orchestration framework
- **GraphState**: State object tracking workflow data (logs, errors, analysis, fixes, NPU stats)
- **RyzenInferenceEngine**: Component that interfaces with AMD Ryzen AI NPU for LLM inference
- **Agent_Workflow**: LangGraph-based workflow with nodes for monitoring, analysis, and fix generation
- **Monitoring_Endpoint**: FastAPI endpoint that triggers the agent workflow
- **Telemetry_Dashboard**: Streamlit-based UI for visualizing NPU hardware metrics
- **Log_Monitor**: Component that reads and processes application log files
- **Error_Analyzer**: Agent node that analyzes detected errors using NPU inference
- **Fix_Generator**: Agent node that generates code fixes using NPU inference

## Requirements

### Requirement 1: Project Structure and Modularity

**User Story:** As a developer, I want a modular folder structure, so that I can easily navigate and maintain different components of the system.

#### Acceptance Criteria

1. THE Aegis_System SHALL organize code into three top-level directories: backend, frontend, and npu_core
2. THE backend directory SHALL contain subdirectories for api, agents, npu, and state modules
3. THE frontend directory SHALL contain the Streamlit dashboard implementation
4. THE npu_core directory SHALL contain NPU-specific inference engine code
5. THE Aegis_System SHALL include configuration files at the project root for dependencies and environment setup

### Requirement 2: LangGraph State Management

**User Story:** As a system architect, I want centralized state management using LangGraph, so that all agent nodes can access and update workflow state consistently.

#### Acceptance Criteria

1. THE Aegis_System SHALL define a GraphState class with typed fields for logs, detected_error, root_cause, suggested_fix, and npu_stats
2. WHEN any agent node executes, THE Aegis_System SHALL pass the current GraphState to that node
3. WHEN an agent node completes, THE Aegis_System SHALL update the GraphState with new information
4. THE GraphState logs field SHALL store a list of log entries as strings
5. THE GraphState detected_error field SHALL store the identified error message as a string
6. THE GraphState root_cause field SHALL store the LLM analysis result as a string
7. THE GraphState suggested_fix field SHALL store the generated code diff as a string
8. THE GraphState npu_stats field SHALL store hardware metrics as a dictionary with latency and utilization keys

### Requirement 3: NPU Integration and Inference Engine

**User Story:** As a system operator, I want LLM inference to run on AMD Ryzen AI NPU hardware, so that I can leverage local hardware acceleration without cloud dependencies.

#### Acceptance Criteria

1. THE Aegis_System SHALL implement a RyzenInferenceEngine class in backend/npu/engine.py
2. THE RyzenInferenceEngine SHALL provide a run_inference method that accepts a prompt string and returns a response string
3. WHEN run_inference is called, THE RyzenInferenceEngine SHALL offload computation to the AMD Ryzen AI NPU
4. WHEN run_inference executes, THE RyzenInferenceEngine SHALL track and return NPU latency in milliseconds
5. WHEN run_inference executes, THE RyzenInferenceEngine SHALL track and return NPU utilization as a percentage
6. WHERE NPU hardware is unavailable, THE RyzenInferenceEngine SHALL provide a mock implementation that simulates processing time
7. THE RyzenInferenceEngine SHALL use ONNX Runtime for NPU inference execution
8. THE RyzenInferenceEngine SHALL load a quantized Llama-3-8B model for inference

### Requirement 4: Agent Workflow Implementation

**User Story:** As a DevOps engineer, I want an automated workflow that monitors logs, analyzes errors, and generates fixes, so that I can reduce manual debugging time.

#### Acceptance Criteria

1. THE Agent_Workflow SHALL implement a monitor_logs node that reads log files and updates GraphState
2. THE Agent_Workflow SHALL implement an analyze_error node that uses NPU inference to determine root causes
3. THE Agent_Workflow SHALL implement a generate_fix node that uses NPU inference to create code diffs
4. WHEN monitor_logs executes, THE Agent_Workflow SHALL parse log files and extract error messages
5. WHEN monitor_logs detects an error, THE Agent_Workflow SHALL update GraphState.detected_error and transition to analyze_error
6. WHEN analyze_error executes, THE Agent_Workflow SHALL call RyzenInferenceEngine with the detected error and update GraphState.root_cause
7. WHEN analyze_error completes, THE Agent_Workflow SHALL transition to generate_fix
8. WHEN generate_fix executes, THE Agent_Workflow SHALL call RyzenInferenceEngine with the root cause and update GraphState.suggested_fix
9. WHEN any node calls RyzenInferenceEngine, THE Agent_Workflow SHALL update GraphState.npu_stats with hardware metrics
10. THE Agent_Workflow SHALL use LangGraph to define node connections and state transitions

### Requirement 5: FastAPI Backend and Monitoring Endpoint

**User Story:** As an API consumer, I want a REST endpoint to trigger monitoring, so that I can integrate the agent into existing DevOps pipelines.

#### Acceptance Criteria

1. THE Aegis_System SHALL implement a FastAPI application in backend/api/main.py
2. THE Aegis_System SHALL expose a POST endpoint at /start-monitoring
3. WHEN /start-monitoring receives a request, THE Monitoring_Endpoint SHALL accept a log_path parameter specifying the log file location
4. WHEN /start-monitoring is called, THE Monitoring_Endpoint SHALL initialize the Agent_Workflow with the provided log path
5. WHEN /start-monitoring is called, THE Monitoring_Endpoint SHALL execute the complete Agent_Workflow
6. WHEN the Agent_Workflow completes, THE Monitoring_Endpoint SHALL return a JSON response containing detected_error, root_cause, suggested_fix, and npu_stats
7. THE Monitoring_Endpoint SHALL return HTTP 200 status code on successful workflow completion
8. IF the workflow encounters an error, THEN THE Monitoring_Endpoint SHALL return HTTP 500 status code with error details

### Requirement 6: Streamlit Telemetry Dashboard

**User Story:** As a system administrator, I want a real-time dashboard showing NPU metrics, so that I can monitor hardware utilization and performance.

#### Acceptance Criteria

1. THE Aegis_System SHALL implement a Streamlit application in frontend/dashboard.py
2. THE Telemetry_Dashboard SHALL display NPU latency metrics in milliseconds
3. THE Telemetry_Dashboard SHALL display NPU utilization percentage
4. THE Telemetry_Dashboard SHALL display the most recent detected error
5. THE Telemetry_Dashboard SHALL display the most recent root cause analysis
6. THE Telemetry_Dashboard SHALL display the most recent suggested fix
7. WHEN new workflow data is available, THE Telemetry_Dashboard SHALL update metrics in real-time
8. THE Telemetry_Dashboard SHALL provide a visual chart showing NPU utilization over time
9. THE Telemetry_Dashboard SHALL provide a button to trigger the monitoring workflow

### Requirement 7: Log Monitoring and Error Detection

**User Story:** As a DevOps engineer, I want automatic log parsing and error detection, so that I can identify issues without manual log review.

#### Acceptance Criteria

1. THE Log_Monitor SHALL read log files from a specified file path
2. WHEN reading logs, THE Log_Monitor SHALL parse each line as a separate log entry
3. WHEN parsing logs, THE Log_Monitor SHALL detect HTTP 500 error patterns
4. WHEN parsing logs, THE Log_Monitor SHALL detect exception stack traces
5. WHEN parsing logs, THE Log_Monitor SHALL detect error-level log messages
6. WHEN an error is detected, THE Log_Monitor SHALL extract the complete error message including context
7. THE Log_Monitor SHALL support common log formats including JSON and plain text
8. IF no errors are detected, THEN THE Log_Monitor SHALL complete without triggering analysis nodes

### Requirement 8: Error Analysis and Root Cause Determination

**User Story:** As a developer, I want AI-powered root cause analysis, so that I can understand why errors occurred without deep debugging.

#### Acceptance Criteria

1. WHEN Error_Analyzer receives a detected error, THE Error_Analyzer SHALL construct a prompt for the LLM
2. THE Error_Analyzer prompt SHALL include the error message and surrounding log context
3. WHEN calling the NPU, THE Error_Analyzer SHALL request analysis of potential root causes
4. WHEN the NPU returns analysis, THE Error_Analyzer SHALL extract the root cause explanation
5. THE Error_Analyzer SHALL format the root cause as a human-readable string
6. THE Error_Analyzer SHALL include relevant code paths or configuration issues in the analysis

### Requirement 9: Fix Generation and Code Diff Creation

**User Story:** As a developer, I want automated fix suggestions with code diffs, so that I can quickly apply corrections to resolve errors.

#### Acceptance Criteria

1. WHEN Fix_Generator receives a root cause, THE Fix_Generator SHALL construct a prompt for the LLM
2. THE Fix_Generator prompt SHALL include the root cause analysis and error context
3. WHEN calling the NPU, THE Fix_Generator SHALL request a code diff or configuration change
4. WHEN the NPU returns a fix, THE Fix_Generator SHALL format it as a unified diff
5. THE Fix_Generator SHALL include file paths and line numbers in the suggested fix
6. THE Fix_Generator SHALL provide explanatory comments in the generated code diff

### Requirement 10: Mock NPU Implementation for Development

**User Story:** As a developer, I want a mock NPU implementation, so that I can develop and test the system without AMD Ryzen AI hardware.

#### Acceptance Criteria

1. WHERE AMD Ryzen AI hardware is not available, THE RyzenInferenceEngine SHALL detect the absence and use mock mode
2. WHEN running in mock mode, THE RyzenInferenceEngine SHALL simulate inference latency between 100-500 milliseconds
3. WHEN running in mock mode, THE RyzenInferenceEngine SHALL return simulated NPU utilization between 40-80 percent
4. WHEN running in mock mode, THE RyzenInferenceEngine SHALL return plausible mock responses for error analysis
5. WHEN running in mock mode, THE RyzenInferenceEngine SHALL return plausible mock responses for fix generation
6. THE mock implementation SHALL maintain the same interface as the real NPU implementation
7. THE Aegis_System SHALL log when operating in mock mode for transparency
