"""
LLM Service Abstraction Layer
Provides unified interface for AWS Bedrock and local dummy LLM services
"""

import json
import time
import random
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class LLMProvider(Enum):
    """Available LLM providers"""
    AWS_BEDROCK = "aws_bedrock"
    DUMMY_LOCAL = "dummy_local"

@dataclass
class LLMRequest:
    """Standard LLM request format"""
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@dataclass
class LLMResponse:
    """Standard LLM response format"""
    content: str
    provider: str
    model: str
    tokens_used: int
    processing_time: float
    success: bool
    error: Optional[str] = None

class LLMServiceInterface(ABC):
    """Abstract interface for LLM services"""
    
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text completion from LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is available"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        pass

class DummyLLMService(LLMServiceInterface):
    """Dummy LLM service for local testing and development"""
    
    def __init__(self):
        self.model_name = "dummy-local-v1.0"
        self.processing_delay = 0.5  # Simulate processing time
        
        # Pre-defined responses for common financial analysis tasks
        self.response_templates = {
            "portfolio_analysis": [
                "Based on the portfolio data provided, I observe a well-diversified allocation across technology, healthcare, and financial sectors. The portfolio shows strong exposure to growth stocks with {total_value} in total assets under management.",
                "The portfolio demonstrates institutional-quality diversification with holdings spanning {num_holdings} different securities. Key observations include significant positions in technology leaders and defensive dividend-paying stocks.",
                "This portfolio reflects a balanced growth strategy with appropriate risk management. The mix of individual stocks, ETFs, and alternative investments suggests sophisticated institutional management."
            ],
            "market_analysis": [
                "Current market conditions show {market_trend} patterns with notable strength in technology and healthcare sectors. The portfolio positioning appears well-suited for the current market environment.",
                "Market analysis indicates favorable conditions for growth-oriented positions. The current allocation shows prudent exposure to market leaders while maintaining defensive characteristics.",
                "The market environment supports the current portfolio strategy, with particular strength in the represented sectors and asset classes."
            ],
            "risk_assessment": [
                "Risk analysis reveals a moderate risk profile with appropriate diversification across asset classes. The portfolio's risk-adjusted returns appear favorable given current market conditions.",
                "The risk characteristics of this portfolio suggest institutional-grade risk management with balanced exposure across growth and defensive positions.",
                "Risk metrics indicate well-controlled downside exposure while maintaining upside participation in key growth sectors."
            ],
            "default": [
                "Thank you for your request. Based on the provided data, I can offer the following analysis and recommendations tailored to your specific portfolio requirements.",
                "I've analyzed the information provided and can offer insights based on current market conditions and portfolio characteristics.",
                "Your request has been processed. Here are my findings based on the data and context provided."
            ]
        }
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a dummy response with realistic delay"""
        start_time = time.time()
        
        # Simulate processing delay
        time.sleep(self.processing_delay)
        
        # Determine response category based on prompt content
        prompt_lower = request.prompt.lower()
        if "portfolio" in prompt_lower and "analysis" in prompt_lower:
            category = "portfolio_analysis"
        elif "market" in prompt_lower:
            category = "market_analysis" 
        elif "risk" in prompt_lower:
            category = "risk_assessment"
        else:
            category = "default"
        
        # Select random response template
        templates = self.response_templates[category]
        base_response = random.choice(templates)
        
        # Add context-aware enhancements if context provided
        if request.context:
            if "total_value" in request.context:
                total_value = f"${request.context['total_value']:,.0f}"
                base_response = base_response.replace("{total_value}", total_value)
            if "num_holdings" in request.context:
                base_response = base_response.replace("{num_holdings}", str(request.context['num_holdings']))
            if "market_trend" in request.context:
                base_response = base_response.replace("{market_trend}", request.context['market_trend'])
        
        # Clean up any unreplaced placeholders
        base_response = base_response.replace("{total_value}", "significant").replace("{num_holdings}", "multiple").replace("{market_trend}", "positive")
        
        # Add system prompt context if provided
        if request.system_prompt:
            base_response = f"{base_response}\n\nNote: {request.system_prompt}"
        
        processing_time = time.time() - start_time
        
        return LLMResponse(
            content=base_response,
            provider="dummy_local",
            model=self.model_name,
            tokens_used=len(base_response.split()) + len(request.prompt.split()),
            processing_time=processing_time,
            success=True
        )
    
    def is_available(self) -> bool:
        """Dummy service is always available"""
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return dummy model information"""
        return {
            "provider": "dummy_local",
            "model": self.model_name,
            "version": "1.0",
            "capabilities": ["text_generation", "financial_analysis", "portfolio_insights"],
            "max_tokens": 4000,
            "cost_per_token": 0.0  # Free for testing
        }

class AWSBedrockService(LLMServiceInterface):
    """AWS Bedrock LLM service integration"""
    
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0", region: str = "us-east-1"):
        self.model_id = model_id
        self.region = region
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client"""
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError, ClientError
            
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region
            )
            
            # Test connection
            self.client.list_foundation_models()
            
        except ImportError:
            print("Warning: boto3 not installed. AWS Bedrock service unavailable.")
            print("Install with: pip install boto3")
            self.client = None
        except (NoCredentialsError, ClientError) as e:
            print(f"Warning: AWS credentials not configured. Bedrock unavailable: {e}")
            self.client = None
        except Exception as e:
            print(f"Warning: Failed to initialize AWS Bedrock client: {e}")
            self.client = None
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text using AWS Bedrock"""
        if not self.client:
            return LLMResponse(
                content="",
                provider="aws_bedrock",
                model=self.model_id,
                tokens_used=0,
                processing_time=0,
                success=False,
                error="AWS Bedrock client not available"
            )
        
        start_time = time.time()
        
        try:
            # Construct the prompt for Claude
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"System: {request.system_prompt}\n\nHuman: {request.prompt}\n\nAssistant:"
            else:
                full_prompt = f"Human: {request.prompt}\n\nAssistant:"
            
            # Prepare request body for Claude
            body = {
                "prompt": full_prompt,
                "max_tokens_to_sample": request.max_tokens,
                "temperature": request.temperature,
                "top_p": 0.9,
                "stop_sequences": ["\n\nHuman:"]
            }
            
            # Call Bedrock
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            content = response_body.get('completion', '').strip()
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                provider="aws_bedrock",
                model=self.model_id,
                tokens_used=len(content.split()) + len(request.prompt.split()),
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return LLMResponse(
                content="",
                provider="aws_bedrock", 
                model=self.model_id,
                tokens_used=0,
                processing_time=processing_time,
                success=False,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if AWS Bedrock is available"""
        return self.client is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get AWS Bedrock model information"""
        return {
            "provider": "aws_bedrock",
            "model": self.model_id,
            "region": self.region,
            "capabilities": ["text_generation", "analysis", "reasoning"],
            "max_tokens": 100000,
            "cost_per_token": 0.000008  # Approximate cost for Claude Sonnet
        }

class LLMServiceManager:
    """Manager for LLM services with automatic fallback"""
    
    def __init__(self, preferred_provider: LLMProvider = LLMProvider.AWS_BEDROCK):
        self.preferred_provider = preferred_provider
        self.services = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all available LLM services"""
        # Always initialize dummy service
        self.services[LLMProvider.DUMMY_LOCAL] = DummyLLMService()
        
        # Initialize AWS Bedrock if requested
        if self.preferred_provider == LLMProvider.AWS_BEDROCK:
            self.services[LLMProvider.AWS_BEDROCK] = AWSBedrockService()
    
    def get_available_service(self) -> LLMServiceInterface:
        """Get the best available LLM service"""
        # Try preferred provider first
        if self.preferred_provider in self.services:
            service = self.services[self.preferred_provider]
            if service.is_available():
                return service
        
        # Fallback to any available service
        for provider, service in self.services.items():
            if service.is_available():
                return service
        
        # Should never happen since dummy is always available
        raise RuntimeError("No LLM services available")
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text using the best available service"""
        service = self.get_available_service()
        return service.generate(request)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all configured services"""
        status = {}
        for provider, service in self.services.items():
            status[provider.value] = {
                "available": service.is_available(),
                "model_info": service.get_model_info()
            }
        return status

# Global LLM service manager instance
llm_manager = LLMServiceManager()

def get_llm_service() -> LLMServiceManager:
    """Get the global LLM service manager"""
    return llm_manager

# Convenience functions
def generate_text(prompt: str, system_prompt: str = None, **kwargs) -> LLMResponse:
    """Generate text using the best available LLM service"""
    request = LLMRequest(
        prompt=prompt,
        system_prompt=system_prompt,
        **kwargs
    )
    return llm_manager.generate(request)

def is_llm_available() -> bool:
    """Check if any LLM service is available"""
    try:
        service = llm_manager.get_available_service()
        return service.is_available()
    except:
        return False