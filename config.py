"""Configuration settings for Aegis-8645 DevOps Agent.

This module provides centralized configuration management using
environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # NPU Settings
    NPU_MODEL_PATH = os.getenv('NPU_MODEL_PATH', 'models/llama-3-8b-quantized.onnx')
    USE_MOCK_NPU = os.getenv('USE_MOCK_NPU', 'true').lower() == 'true'
    
    # API Settings
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '8000'))
    
    # Dashboard Settings
    DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '8501'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent
    EXAMPLES_DIR = PROJECT_ROOT / 'examples'
    MODELS_DIR = PROJECT_ROOT / 'models'
    
    @classmethod
    def get_log_level(cls):
        """Get logging level as integer."""
        import logging
        return getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)


# Create singleton instance
config = Config()
