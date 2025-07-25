# Google Agent2Agent (A2A) Protocol Example

This project demonstrates Google's Agent2Agent Protocol, showing how AI agents can communicate and collaborate across different systems using standardized JSON-RPC 2.0 messages.

## Overview

The example implements a complete **portfolio analysis system** with four specialized agents:
- **ClientDataAgent**: Provides client portfolio and holdings data
- **FinancialDataAgent**: Real-time market data and stock prices  
- **ChartGenerationAgent**: Creates portfolio visualizations and charts
- **DataProcessor**: General data processing and analysis

## Key A2A Protocol Features

- ✅ **Capability Discovery**: Agents advertise their capabilities via Agent Cards
- ✅ **JSON-RPC 2.0**: Standardized message format for agent communication  
- ✅ **Task Delegation**: Agents can delegate work to specialized agents
- ✅ **Multi-Agent Workflows**: Coordinate complex processes across agents
- ✅ **Error Handling**: Standardized error codes and responses
- ✅ **Modality Support**: Text, JSON, and extensible to audio/video

## Quick Start

1. **Install Dependencies**
   ```bash
   # Option 1: Using uv
   python -m uv pip install -r requirements.txt
   
   # Option 2: Using standard pip
   pip install -r requirements.txt
   ```

2. **Start All Agents** (in separate terminals)
   ```bash
   # Terminal 1: Client Data Agent
   python client_data_agent.py
   
   # Terminal 2: Financial Data Agent  
   python financial_data_agent.py
   
   # Terminal 3: Chart Generation Agent
   python chart_generation_agent.py
   
   # Terminal 4: Data Processor Agent
   python data_processor_agent.py
   ```

3. **Start Web UI** (in another terminal)
   ```bash
   python web_ui.py
   # Then open: http://localhost:5000
   ```

4. **Try the Portfolio Analysis**
   - Click "Portfolio Analysis" for complete workflow
   - Click "Top Holdings Chart" for interactive charts
   - Click "Portfolio Pie Chart" for allocation visualization

## File Structure

```
├── a2a_protocol.py           # Core A2A protocol implementation
├── client_data_agent.py      # Client portfolio data provider (Port 8003)
├── financial_data_agent.py   # Market data and stock prices (Port 8004)
├── chart_generation_agent.py # Interactive chart generator (Port 8005)
├── data_processor_agent.py   # General data processing (Port 8002)
├── agent_coordinator.py      # Task coordinator agent
├── demo_a2a.py              # Command line demonstration script
├── web_ui.py                # Web UI dashboard (Port 5000)
├── templates/
│   └── dashboard.html       # Interactive web dashboard
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore file
└── README.md                # This file
```

## A2A Protocol Messages

### Agent Capability Discovery
```json
{
  "jsonrpc": "2.0",
  "method": "get_capabilities",
  "params": {},
  "id": "discover_1234"
}
```

### Portfolio Analysis Task
```json
{
  "jsonrpc": "2.0", 
  "method": "execute_task",
  "params": {
    "task_id": "portfolio_task_5678",
    "task_type": "aggregate_holdings",
    "data": {},
    "context": {
      "requester": "WebUI",
      "priority": "high"
    }
  },
  "id": "portfolio_task_5678"
}
```

### Chart Generation Task
```json
{
  "jsonrpc": "2.0",
  "method": "execute_task", 
  "params": {
    "task_id": "chart_task_9012",
    "task_type": "generate_top_holdings_chart",
    "data": {
      "holdings": [...],
      "title": "Top 10 Client Holdings"
    },
    "context": {
      "requester": "WebUI",
      "priority": "medium"
    }
  },
  "id": "chart_task_9012"
}
```

## Agent Cards

Each agent advertises its capabilities through an Agent Card:

### ClientDataAgent
```json
{
  "name": "ClientDataAgent",
  "description": "Provides client portfolio data, holdings, and account information",
  "version": "1.0",
  "endpoint": "http://localhost:8003",
  "capabilities": [
    "get_client_portfolio",
    "get_client_holdings", 
    "get_all_client_data",
    "aggregate_holdings",
    "client_portfolio_summary"
  ]
}
```

### FinancialDataAgent
```json
{
  "name": "FinancialDataAgent",
  "description": "Provides real-time market data, stock prices, and financial product information",
  "version": "1.0",
  "endpoint": "http://localhost:8004",
  "capabilities": [
    "get_stock_price",
    "get_market_data",
    "get_portfolio_values",
    "calculate_market_values"
  ]
}
```

### ChartGenerationAgent
```json
{
  "name": "ChartGenerationAgent", 
  "description": "Creates portfolio analysis charts, graphs, and visual reports",
  "version": "1.0",
  "endpoint": "http://localhost:8005",
  "capabilities": [
    "generate_portfolio_pie_chart",
    "generate_holdings_bar_chart",
    "generate_top_holdings_chart",
    "generate_interactive_dashboard"
  ]
}
```

## Demo Scenarios

The demonstration includes multiple scenarios:

1. **Portfolio Analysis**: Complete multi-agent workflow showing:
   - Client data aggregation across 3 portfolios
   - Real-time market price calculation  
   - Interactive chart generation with top 10 holdings

2. **Capability Discovery**: How agents discover each other's capabilities across the network

3. **Individual Chart Generation**: 
   - Top Holdings Bar Chart (interactive with hover details)
   - Portfolio Pie Chart (allocation percentages)
   
4. **Custom Task Execution**: Send specific tasks to any agent via the web interface

## Web Dashboard Features

- 🤖 **Real-time Agent Status**: Monitor which agents are online/offline (4 agents total)
- 📡 **Live Message Log**: View A2A protocol messages as they happen between agents
- 📈 **Interactive Portfolio Charts**: Beautiful Plotly.js charts with real portfolio data
- 💰 **Portfolio Summary Cards**: Total value, holdings count, largest positions
- 🔍 **Multi-Agent Workflows**: Watch agents collaborate on complex tasks
- ⚙️ **Custom Tasks**: Send tasks to ClientData, FinancialData, or ChartGeneration agents
- 📊 **Real-time Stats**: Track message counts and agent activity across the network

## Portfolio Analysis Workflow

1. **ClientDataAgent** aggregates holdings from multiple client portfolios:
   - John Smith: $850K portfolio with AAPL, MSFT, GOOGL positions
   - Sarah Johnson: $1.2M portfolio with tech and dividend stocks  
   - Michael Chen: $650K portfolio focused on tech stocks

2. **FinancialDataAgent** provides real-time market data:
   - Current stock prices with simulated fluctuations
   - Market cap and sector information
   - Portfolio value calculations

3. **ChartGenerationAgent** creates interactive visualizations:
   - Top 10 holdings with market values and percentages
   - Sector allocation charts
   - Performance analysis with gain/loss indicators

## Architecture

```
                    Google A2A Protocol (JSON-RPC 2.0 over HTTP)
                              
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  ClientDataAgent│    │ FinancialDataAgent│    │ChartGeneration │
│    Port 8003    │    │    Port 8004     │    │   Port 8005     │
│                 │    │                  │    │                 │
│ - Client Data   │    │ - Stock Prices   │    │ - Plotly Charts │
│ - Holdings      │    │ - Market Data    │    │ - Visualizations│
│ - Portfolios    │    │ - Calculations   │    │ - Dashboards    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────▼──────────────┐
                    │     Web UI Dashboard       │
                    │       Port 5000            │
                    │                            │
                    │ - Real-time Monitoring     │
                    │ - Interactive Charts       │
                    │ - A2A Message Logging      │
                    │ - Multi-Agent Coordination │
                    └────────────────────────────┘
```

## Key Benefits of A2A Protocol

- **Interoperability**: Agents from different vendors can communicate seamlessly
- **Standardization**: Based on proven JSON-RPC 2.0 standard with HTTP transport
- **Enterprise-Ready**: Built-in security, authentication, and error handling
- **Scalable**: Supports long-running tasks and complex multi-agent workflows
- **Extensible**: Easy to add new capabilities, agents, and communication modalities
- **Real-world Application**: Demonstrates practical portfolio analysis use case

## Sample Portfolio Data

The system includes realistic test data:

**Client Portfolios:**
- **3 clients** with diversified portfolios totaling **$2.7M**
- **21 unique holdings** including AAPL, MSFT, GOOGL, NVDA, TSLA
- **Multiple sectors**: Technology, Healthcare, Financial Services, Consumer, ETFs
- **Real-time pricing** with simulated market fluctuations

**Top Holdings Example:**
1. GOOGL: $687K (21.9%) - Technology sector leader
2. NVDA: $605K (19.2%) - AI/Semiconductor growth  
3. MSFT: $415K (13.2%) - Enterprise software
4. AAPL: $291K (9.2%) - Consumer electronics
5. And more diversified positions...

## Technology Stack

- **Backend**: Python, Flask for agent servers
- **Protocol**: Google A2A (JSON-RPC 2.0 over HTTP)
- **Frontend**: HTML5, JavaScript, Plotly.js for interactive charts
- **Data**: Pandas, NumPy for financial calculations
- **Communication**: HTTP REST APIs with A2A message format

## Next Steps

- Explore the [official A2A specification](https://github.com/google/A2A)
- Add authentication and security features
- Implement real market data APIs (Alpha Vantage, Yahoo Finance)
- Scale to multiple agent instances with load balancing
- Add more chart types (candlestick, performance over time)
- Integrate with enterprise portfolio management systems

## Related Projects

- [Google's official A2A repository](https://github.com/google/A2A)
- [A2A Protocol documentation](https://a2a-protocol.org)
- [Anthropic's MCP](https://github.com/anthropics/mcp) (complementary protocol for tool integration)