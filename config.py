"""
Configuration file for the Multi-Agent Market Research System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the application"""
    
    # API Keys - with automatic whitespace trimming
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
    KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME", "").strip()
    KAGGLE_KEY = os.getenv("KAGGLE_KEY", "").strip()
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "").strip()
    
    # Application Settings
    MAX_SEARCH_RESULTS = 50
    MAX_DATASETS_PER_PLATFORM = 5
    OUTPUT_DIR = "output"
    REPORTS_DIR = "reports"
    
    # Rate Limiting & Resource Management
    MAX_CONCURRENT_REQUESTS = 3
    REQUEST_TIMEOUT = 30  # seconds
    RATE_LIMIT_DELAY = 1  # seconds between requests
    MAX_RETRIES = 3
    MEMORY_LIMIT_MB = 512  # Memory limit for processing
    
    # Agent Settings - Optimized for speed and efficiency
    TEMPERATURE = 0.3  # Lower temperature for more focused, consistent reasoning
    MAX_TOKENS = 4000  # Reduced for faster processing
    MODEL_NAME = "gpt-4o"  # Latest and most capable model
    REASONING_TEMPERATURE = 0.1  # Very low temperature for critical reasoning tasks
    CREATIVE_TEMPERATURE = 0.7  # Higher temperature for creative use case generation
    
    # Fast Mode Settings
    FAST_MODE_MAX_TOKENS = 2000  # Even faster for fast mode
    FAST_MODE_TEMPERATURE = 0.2  # More focused for speed
    
    @classmethod
    def validate_config(cls):
        """Validate that required environment variables are set and properly formatted"""
        required_vars = [
            "OPENAI_API_KEY",
            "TAVILY_API_KEY"
        ]
        
        missing_vars = []
        invalid_vars = []
        
        for var in required_vars:
            value = getattr(cls, var)
            if not value or value.strip() == "":
                missing_vars.append(var)
            elif var == "OPENAI_API_KEY" and not value.strip().startswith("sk-"):
                invalid_vars.append(f"{var} (must start with 'sk-')")
            elif var == "TAVILY_API_KEY" and not value.strip().startswith("tvly-"):
                invalid_vars.append(f"{var} (must start with 'tvly-')")
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        if invalid_vars:
            raise ValueError(f"Invalid API key format: {', '.join(invalid_vars)}")
        
        return True
    
    @classmethod
    def get_api_status(cls):
        """Get detailed API key status for debugging"""
        status = {}
        for var in ["OPENAI_API_KEY", "TAVILY_API_KEY", "KAGGLE_USERNAME", "KAGGLE_KEY", "GITHUB_TOKEN", "HUGGINGFACE_TOKEN"]:
            value = getattr(cls, var)
            if value:
                if var in ["OPENAI_API_KEY", "TAVILY_API_KEY"]:
                    status[var] = f"Set (ends with ...{value[-4:]})"
                else:
                    status[var] = "Set"
            else:
                status[var] = "Not set"
        return status

# Create output directories
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
os.makedirs(Config.REPORTS_DIR, exist_ok=True)