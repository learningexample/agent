"""
LLM Service Configuration
Centralized configuration for LLM services
"""

import os
from enum import Enum
from typing import Dict, Any

class LLMProvider(Enum):
    """Available LLM providers"""
    AWS_BEDROCK = "aws_bedrock"
    DUMMY_LOCAL = "dummy_local"

class LLMConfig:
    """Configuration class for LLM services"""
    
    def __init__(self):
        # Default configuration
        self.config = {
            "preferred_provider": os.getenv("LLM_PROVIDER", "dummy_local"),
            "aws_bedrock": {
                "model_id": os.getenv("AWS_BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"),
                "region": os.getenv("AWS_REGION", "us-east-1"),
                "max_tokens": int(os.getenv("AWS_BEDROCK_MAX_TOKENS", "1000")),
                "temperature": float(os.getenv("AWS_BEDROCK_TEMPERATURE", "0.7"))
            },
            "dummy_local": {
                "model_name": "dummy-local-v1.0",
                "processing_delay": float(os.getenv("DUMMY_PROCESSING_DELAY", "0.5")),
                "max_tokens": int(os.getenv("DUMMY_MAX_TOKENS", "4000"))
            }
        }
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider"""
        return self.config.get(provider, {})
    
    def get_preferred_provider(self) -> str:
        """Get preferred LLM provider"""
        return self.config["preferred_provider"]
    
    def set_preferred_provider(self, provider: str):
        """Set preferred LLM provider"""
        if provider in ["aws_bedrock", "dummy_local"]:
            self.config["preferred_provider"] = provider
        else:
            raise ValueError(f"Invalid provider: {provider}")
    
    def is_aws_configured(self) -> bool:
        """Check if AWS credentials are likely configured"""
        return (
            os.getenv("AWS_ACCESS_KEY_ID") is not None or
            os.getenv("AWS_PROFILE") is not None or
            os.path.exists(os.path.expanduser("~/.aws/credentials"))
        )
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment configuration info"""
        return {
            "preferred_provider": self.get_preferred_provider(),
            "aws_configured": self.is_aws_configured(),
            "aws_region": self.config["aws_bedrock"]["region"],
            "aws_model": self.config["aws_bedrock"]["model_id"],
            "environment_variables": {
                "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
                "AWS_REGION": os.getenv("AWS_REGION"),
                "AWS_BEDROCK_MODEL_ID": os.getenv("AWS_BEDROCK_MODEL_ID")
            }
        }

# Global configuration instance
llm_config = LLMConfig()

def get_llm_config() -> LLMConfig:
    """Get the global LLM configuration"""
    return llm_config