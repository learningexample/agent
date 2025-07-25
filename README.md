# Google Agent2Agent (A2A) Protocol Example

This project demonstrates Google's Agent2Agent Protocol, showing how AI agents can communicate and collaborate across different systems using standardized JSON-RPC 2.0 messages.

## Overview

The example implements two specialized agents:
- **TaskCoordinator**: Orchestrates complex tasks and delegates work
- **DataProcessor**: Specializes in data analysis and processing

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

2. **Start the DataProcessor Agent**
   ```bash
   python data_processor_agent.py
   ```

3. **Run the Demo** (in another terminal)
   ```bash
   # Command line demo
   python demo_a2a.py
   
   # Web UI dashboard
   python web_ui.py
   # Then open: http://localhost:5000
   ```

## File Structure

```
├── a2a_protocol.py           # Core A2A protocol implementation
├── agent_coordinator.py      # Task coordinator agent
├── data_processor_agent.py   # Data processing specialist agent  
├── demo_a2a.py              # Command line demonstration script
├── web_ui.py                # Web UI for interactive demonstration
├── templates/
│   └── dashboard.html       # Web dashboard interface
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## A2A Protocol Messages

### Agent Capability Discovery
```json
{
  "jsonrpc": "2.0",
  "method": "agent.get_capabilities",
  "params": {},
  "id": "discover_1234"
}
```

### Task Delegation
```json
{
  "jsonrpc": "2.0", 
  "method": "execute_task",
  "params": {
    "task_id": "task_5678",
    "task_type": "data_analysis",
    "data": {
      "dataset": "sales_data.csv",
      "operations": ["clean", "aggregate", "trend_analysis"]
    },
    "context": {
      "requester": "TaskCoordinator",
      "priority": "high"
    }
  },
  "id": "task_5678"
}
```

## Agent Cards

Each agent advertises its capabilities through an Agent Card:

```json
{
  "name": "DataProcessor",
  "description": "Specialized agent for data processing and analysis",
  "version": "1.0",
  "endpoint": "http://localhost:8002",
  "capabilities": [
    "data_cleaning",
    "statistical_analysis", 
    "trend_detection"
  ],
  "supported_modalities": ["text", "json"],
  "authentication_schemes": ["none", "bearer"]
}
```

## Demo Scenarios

The demonstration shows:

1. **Capability Discovery**: How agents discover each other's capabilities
2. **Task Delegation**: A coordinator delegating data analysis to a specialist
3. **Multi-Agent Workflow**: Complex business process across multiple agents

## Web Dashboard Features

- 🤖 **Real-time Agent Status**: Monitor which agents are online/offline
- 📡 **Live Message Log**: View A2A protocol messages as they happen
- 🔍 **Interactive Demos**: Run capability discovery, data analysis, and workflows
- ⚙️ **Custom Tasks**: Send custom tasks to agents via web interface
- 📈 **Real-time Stats**: Track message counts and agent activity

## Architecture

```
┌─────────────────┐    A2A Protocol    ┌──────────────────┐
│ TaskCoordinator │ ──────────────────→ │  DataProcessor   │
│                 │ ←────────────────── │                  │
│ - Task Planning │   JSON-RPC 2.0     │ - Data Cleaning  │
│ - Coordination  │   HTTP/HTTPS        │ - Analysis       │
│ - Aggregation   │                     │ - Trend Detection│
└─────────────────┘                     └──────────────────┘
```

## Key Benefits of A2A Protocol

- **Interoperability**: Agents from different vendors can communicate
- **Standardization**: Based on proven JSON-RPC 2.0 standard
- **Enterprise-Ready**: Built-in security and authentication support
- **Scalable**: Supports long-running tasks and complex workflows
- **Extensible**: Easy to add new capabilities and modalities

## Next Steps

- Explore the [official A2A specification](https://github.com/google/A2A)
- Add authentication and security features
- Implement audio/video modality support
- Scale to multiple agent instances
- Integrate with enterprise systems

## Related Projects

- [Google's official A2A repository](https://github.com/google/A2A)
- [A2A Protocol documentation](https://a2a-protocol.org)
- [Anthropic's MCP](https://github.com/anthropics/mcp) (complementary protocol)