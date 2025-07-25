"""
Demo script for LLM-enhanced portfolio analysis
Shows how to use the new LLM layer with both dummy and AWS Bedrock services
"""

import json
import time
import requests
from llm_service import get_llm_service, generate_text, LLMProvider
from llm_config import get_llm_config

def test_llm_service():
    """Test the LLM service directly"""
    print("Testing LLM Service Layer")
    print("=" * 50)
    
    llm_service = get_llm_service()
    config = get_llm_config()
    
    # Show service status
    print("LLM Service Status:")
    status = llm_service.get_service_status()
    for provider, info in status.items():
        print(f"  {provider}: {'✅ Available' if info['available'] else '❌ Unavailable'}")
        print(f"    Model: {info['model_info']['model']}")
        print(f"    Provider: {info['model_info']['provider']}")
    
    print(f"\nEnvironment Info:")
    env_info = config.get_environment_info()
    print(f"  Preferred Provider: {env_info['preferred_provider']}")
    print(f"  AWS Configured: {'✅' if env_info['aws_configured'] else '❌'}")
    
    # Test text generation
    print(f"\n🚀 Testing Text Generation")
    print("-" * 30)
    
    test_prompt = """
    Analyze this sample portfolio:
    - AAPL: $500M (25%)
    - MSFT: $400M (20%) 
    - GOOGL: $300M (15%)
    - Bonds: $800M (40%)
    
    Provide a brief risk assessment.
    """
    
    try:
        response = generate_text(
            prompt=test_prompt,
            system_prompt="You are a senior portfolio analyst.",
            max_tokens=500,
            temperature=0.3
        )
        
        print(f"✅ Generation successful!")
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Tokens: {response.tokens_used}")
        print(f"Time: {response.processing_time:.2f}s")
        print(f"\nResponse:")
        print("-" * 20)
        print(response.content)
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")

def test_portfolio_analysis_agent():
    """Test the Portfolio Analysis Agent"""
    print(f"\n🤖 Testing Portfolio Analysis Agent")
    print("=" * 50)
    
    # Check if agent is running
    agent_url = "http://localhost:8006"
    
    try:
        # Health check
        health_response = requests.get(f"{agent_url}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Agent is healthy!")
            print(f"  Agent: {health_data['agent']}")
            print(f"  LLM Available: {'✅' if health_data['llm_available'] else '❌'}")
            
            # Show LLM status
            llm_status = health_data.get('llm_status', {})
            for provider, info in llm_status.items():
                print(f"  {provider}: {'✅' if info['available'] else '❌'}")
        else:
            print(f"❌ Agent health check failed: {health_response.status_code}")
            return
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Portfolio Analysis Agent at {agent_url}")
        print(f"   Make sure to start it with: python portfolio_analysis_agent.py")
        print(f"   Error: {e}")
        return
    
    # Test portfolio analysis
    print(f"\n📊 Testing Portfolio Analysis")
    print("-" * 30)
    
    # Sample portfolio data
    sample_holdings = [
        {"symbol": "AAPL", "market_value": 500000000, "shares": 2500000},
        {"symbol": "MSFT", "market_value": 400000000, "shares": 1000000},
        {"symbol": "GOOGL", "market_value": 300000000, "shares": 100000},
        {"symbol": "SPY", "market_value": 200000000, "shares": 400000},
        {"symbol": "TLT", "market_value": 800000000, "shares": 8000000}
    ]
    
    analysis_request = {
        "jsonrpc": "2.0",
        "method": "execute_task",
        "params": {
            "task_id": f"demo_analysis_{int(time.time())}",
            "task_type": "portfolio_analysis_llm",
            "data": {
                "client_id": "CLIENT001",
                "holdings": sample_holdings
            },
            "context": {
                "requester": "Demo Script",
                "priority": "high"
            }
        },
        "id": f"demo_{int(time.time())}"
    }
    
    try:
        response = requests.post(
            f"{agent_url}/a2a",
            json=analysis_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis completed!")
            
            if "result" in result and result["result"]:
                analysis_data = result["result"]["result"]
                metadata = analysis_data.get("analysis_metadata", {})
                
                print(f"  Client: {analysis_data.get('client_name', 'Unknown')}")
                print(f"  Portfolio Value: ${analysis_data.get('portfolio_summary', {}).get('total_value', 0):,.0f}")
                print(f"  LLM Provider: {metadata.get('provider', 'Unknown')}")
                print(f"  Processing Time: {metadata.get('processing_time', 0):.2f}s")
                print(f"  Tokens Used: {metadata.get('tokens_used', 0)}")
                
                print(f"\n📝 LLM Analysis:")
                print("-" * 20)
                print(analysis_data.get("llm_analysis", "No analysis available"))
                
            else:
                print(f"❌ No analysis result in response")
                print(f"Response: {json.dumps(result, indent=2)}")
                
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️ Analysis request timed out (this is normal for first AWS Bedrock calls)")
    except Exception as e:
        print(f"❌ Analysis request failed: {e}")

def show_usage_examples():
    """Show usage examples"""
    print(f"\n📚 Usage Examples")
    print("=" * 50)
    
    print("""
🔧 Configuration Options:

1. Use Dummy Local Service (default):
   export LLM_PROVIDER=dummy_local

2. Use AWS Bedrock:
   export LLM_PROVIDER=aws_bedrock
   export AWS_REGION=us-east-1
   export AWS_BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
   
   # Ensure AWS credentials are configured:
   aws configure  # or use IAM roles, AWS SSO, etc.

🚀 Running the Services:

1. Start Portfolio Analysis Agent:
   python portfolio_analysis_agent.py

2. Test the LLM services:
   python demo_llm_analysis.py

3. Use in Web UI:
   python web_ui.py
   # Then visit http://localhost:5000

📊 Available LLM-Enhanced Capabilities:

- portfolio_analysis_llm: Comprehensive AI-powered portfolio analysis
- market_commentary: AI market insights and outlook  
- risk_assessment_llm: AI-driven risk analysis
- investment_insights: Strategic AI recommendations

🔄 A2A Protocol Integration:

The new agent seamlessly integrates with existing A2A protocol:
- Discoverable capabilities via get_capabilities
- Standard JSON-RPC 2.0 message format
- Compatible with existing web dashboard
- Automatic fallback from AWS Bedrock to dummy service
    """)

def main():
    """Main demo function"""
    print("LLM-Enhanced A2A Portfolio Analysis Demo")
    print("=" * 60)
    
    # Test LLM service layer
    test_llm_service()
    
    # Test portfolio analysis agent (if running)
    test_portfolio_analysis_agent()
    
    # Show usage examples
    show_usage_examples()
    
    print(f"\n✨ Demo completed!")
    print("Next steps:")
    print("1. Start the portfolio analysis agent: python portfolio_analysis_agent.py")
    print("2. Test via web UI at http://localhost:5000")
    print("3. Configure AWS Bedrock for production AI analysis")

if __name__ == "__main__":
    main()