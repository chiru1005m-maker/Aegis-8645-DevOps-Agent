# Aegis-8645 DevOps Agent

A Self-Healing DevOps Agent that monitors application logs, detects errors, analyzes root causes, and suggests fixes using local LLM inference on AMD Ryzen AI NPU hardware.

## Features

- **Automated Log Monitoring**: Reads and parses log files in plain text and JSON formats
- **Error Detection**: Identifies HTTP 500 errors, exceptions, and ERROR-level log messages
- **AI-Powered Analysis**: Uses local LLM inference to determine root causes
- **Fix Generation**: Automatically generates code fixes in unified diff format
- **NPU Acceleration**: Leverages AMD Ryzen AI NPU for fast local inference
- **Real-time Dashboard**: Streamlit-based UI for monitoring and visualization
- **REST API**: FastAPI backend for integration with existing DevOps pipelines

## Architecture

- **Backend**: FastAPI with LangGraph agent orchestration
- **Frontend**: Streamlit dashboard for real-time telemetry
- **Inference**: ONNX Runtime with AMD Ryzen AI NPU (mock mode for development)
- **Model**: Llama-3-8B (quantized)

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd aegis-8645
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Running the Backend API

Start the FastAPI server:

```bash
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

Or use the Python script directly:

```bash
python backend/api/main.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Running the Dashboard

Start the Streamlit dashboard:

```bash
streamlit run frontend/dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Using the API

**Start Monitoring Endpoint:**

```bash
curl -X POST http://localhost:8000/start-monitoring \
  -H "Content-Type: application/json" \
  -d '{"log_path": "examples/sample_error.log"}'
```

**Response:**

```json
{
  "status": "completed",
  "detected_error": "HTTP 500 Internal Server Error at /api/users/456",
  "root_cause": "NullPointerException due to missing user validation...",
  "suggested_fix": "--- a/api/users.py\n+++ b/api/users.py\n...",
  "npu_stats": {
    "latency_ms": 245.3,
    "utilization_percent": 67.5
  }
}
```

## Sample Log Files

The `examples/` directory contains sample log files for testing:

- `sample_error.log` - Contains HTTP 500 errors
- `sample_exception.log` - Contains Python exception stack traces
- `sample_clean.log` - Clean logs with no errors
- `sample_json.log` - JSON-formatted logs with errors

## NPU Modes

### Mock Mode (Default)

For development without AMD Ryzen AI hardware:

- Set `USE_MOCK_NPU=true` in `.env`
- Simulates inference latency (100-500ms)
- Returns plausible mock responses

### Real NPU Mode

For production with AMD Ryzen AI hardware:

- Set `USE_MOCK_NPU=false` in `.env`
- Set `NPU_MODEL_PATH` to your ONNX model location
- Requires AMD Ryzen AI NPU hardware and drivers

## Configuration

Edit `.env` file to configure:

```bash
# NPU Settings
NPU_MODEL_PATH=models/llama-3-8b-quantized.onnx
USE_MOCK_NPU=true

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Dashboard Settings
DASHBOARD_PORT=8501

# Logging
LOG_LEVEL=INFO
```

## Project Structure

```
aegis-8645/
├── backend/
│   ├── agents/          # LangGraph workflow nodes
│   │   ├── monitor.py   # Log monitoring
│   │   ├── analyzer.py  # Error analysis
│   │   ├── generator.py # Fix generation
│   │   └── workflow.py  # LangGraph orchestration
│   ├── api/             # FastAPI application
│   │   ├── main.py      # API endpoints
│   │   └── models.py    # Pydantic models
│   ├── npu/             # NPU integration
│   │   └── engine.py    # RyzenInferenceEngine
│   └── state/           # State management
│       └── graph_state.py
├── frontend/
│   └── dashboard.py     # Streamlit dashboard
├── examples/            # Sample log files
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
└── README.md
```

## Development

### Running Tests

```bash
pytest
```

### Code Coverage

```bash
pytest --cov=backend --cov=frontend
```

## Troubleshooting

### Backend API Not Starting

- Check if port 8000 is already in use
- Verify Python dependencies are installed
- Check logs for error messages

### Dashboard Cannot Connect to API

- Ensure backend API is running on `http://localhost:8000`
- Check firewall settings
- Verify API_BASE_URL in dashboard.py

### NPU Not Detected

- Verify AMD Ryzen AI drivers are installed
- Check ONNX Runtime installation
- Use mock mode for development: `USE_MOCK_NPU=true`

## License

[Your License Here]

## Contributing

[Contributing Guidelines Here]

## Support

For issues and questions, please open an issue on GitHub.
