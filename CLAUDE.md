# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Python Environment Setup
```bash
# Install dependencies using uv (preferred)
python -m uv pip install -r requirements.txt

# Or using standard pip
pip install -r requirements.txt
```

### Running the Application
Start all agents in separate terminals:
```bash
# Terminal 1: Client Data Agent (Port 8003)
python client_data_agent.py

# Terminal 2: Financial Data Agent (Port 8004)  
python financial_data_agent.py

# Terminal 3: Chart Generation Agent (Port 8005)
python chart_generation_agent.py

# Terminal 4: Data Processor Agent (Port 8002)
python data_processor_agent.py

# Terminal 5: LLM-Enhanced Portfolio Analysis Agent (Port 8006)
python portfolio_analysis_agent.py

# Terminal 6: Web UI Dashboard (Port 5000)
python web_ui.py
```

### LLM Service Configuration
Configure LLM services using environment variables:

```bash
# For local development (default)
export LLM_PROVIDER=dummy_local

# For AWS Bedrock production
export LLM_PROVIDER=aws_bedrock
export AWS_REGION=us-east-1
export AWS_BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Ensure AWS credentials are configured
aws configure
```

### Testing
```bash
# Run integration tests
python test_csv_integration.py

# Run demo scenarios
python demo_a2a.py

# Test LLM-enhanced analysis
python demo_llm_analysis.py
```

## Architecture Overview

This is a Google Agent2Agent (A2A) Protocol demonstration implementing a portfolio analysis system with specialized agents communicating via JSON-RPC 2.0 over HTTP.

### Core Components

1. **A2A Protocol Core** (`a2a_protocol.py`):
   - `A2AProtocolClient`: Client for sending requests to agents
   - `A2AProtocolServer`: Base server implementation for agents
   - `A2AMessage`: JSON-RPC 2.0 message structure
   - `AgentCard`: Capability advertisement system
   - `A2ATaskManager`: Long-running task management

2. **Specialized Agents** (Ports 8002-8006):
   - **ClientDataAgent**: Client portfolio and holdings data
   - **FinancialDataAgent**: Real-time market data and calculations
   - **ChartGenerationAgent**: Interactive Plotly.js visualizations
   - **DataProcessor**: General data processing and analysis
   - **PortfolioAnalysisAgent**: LLM-enhanced portfolio analysis and insights

3. **Web Dashboard** (`web_ui.py` - Port 5000):
   - Real-time agent status monitoring
   - A2A protocol message logging
   - Interactive portfolio charts
   - Multi-agent workflow coordination

4. **Agent Coordinator** (`agent_coordinator.py`):
   - Task delegation and workflow coordination
   - Agent discovery and registration
   - Complex multi-step task orchestration

5. **LLM Service Layer** (`llm_service.py`):
   - **LLMServiceInterface**: Abstract interface for LLM providers
   - **AWSBedrockService**: AWS Bedrock integration (Claude, etc.)
   - **DummyLLMService**: Local testing service with realistic responses
   - **LLMServiceManager**: Automatic provider selection and fallback

### Agent Communication Pattern

Agents communicate using standardized A2A protocol messages:
- **Capability Discovery**: `get_capabilities` method
- **Task Execution**: `execute_task` method with task_id, task_type, data, and context
- **Health Checks**: `/health` endpoint for status monitoring
- **Error Handling**: JSON-RPC 2.0 compliant error codes

### Data Flow Architecture

```
CSV Data → ClientDataAgent → FinancialDataAgent → ChartGenerationAgent
    ↓              ↓                 ↓                    ↓
Portfolio     Market Data      Value Calc         Interactive Charts
Holdings      Stock Prices     Aggregation        Plotly.js Visuals
```

The web UI orchestrates multi-agent workflows by sending sequential A2A messages and aggregating responses for the dashboard.

### Key Design Patterns

- **Agent Discovery**: Agents advertise capabilities via Agent Cards
- **Task Delegation**: Coordinator agents delegate specialized work
- **Message Logging**: All A2A communications are logged for debugging
- **Concurrent Health Checks**: Agent status checked in parallel using ThreadPoolExecutor
- **Error Propagation**: JSON-RPC 2.0 error codes bubble up through the system

### LLM-Enhanced Capabilities

The PortfolioAnalysisAgent provides AI-powered analysis through these capabilities:

- **portfolio_analysis_llm**: Comprehensive portfolio analysis with AI insights
- **market_commentary**: AI-generated market outlook and positioning advice  
- **risk_assessment_llm**: Intelligent risk analysis and recommendations
- **investment_insights**: Strategic investment themes and next steps

### Development Notes

- Each agent runs on a dedicated port (8002-8006)
- Web UI serves as the orchestration layer on port 5000
- All agents implement `/a2a` endpoint for protocol communication
- CSV data is stored in `data/` directory
- Generated charts are cached in memory (excluded from git)
- LLM services automatically fallback from AWS Bedrock to dummy service
- Configure LLM provider via `LLM_PROVIDER` environment variable