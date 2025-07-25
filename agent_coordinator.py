"""
Google Agent2Agent Protocol Example - Task Coordinator Agent
This agent coordinates tasks and delegates work to specialized agents.
"""

import json
import requests
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class A2AMessage:
    """A2A Protocol Message Structure"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = None
    id: str = ""

@dataclass
class AgentCard:
    """Agent capability advertisement"""
    name: str
    description: str
    capabilities: list
    endpoint: str
    version: str = "1.0"

class TaskCoordinatorAgent:
    """Agent that coordinates complex tasks using A2A protocol"""
    
    def __init__(self, name: str, port: int = 8001):
        self.name = name
        self.port = port
        self.endpoint = f"http://localhost:{port}"
        self.tasks = {}
        self.known_agents = {}
        
        # Agent card for capability discovery
        self.agent_card = AgentCard(
            name="TaskCoordinator",
            description="Coordinates complex tasks across multiple specialized agents",
            capabilities=[
                "task_planning",
                "agent_discovery", 
                "workflow_coordination",
                "result_aggregation"
            ],
            endpoint=self.endpoint
        )
    
    def register_agent(self, agent_card: AgentCard):
        """Register a known agent for task delegation"""
        self.known_agents[agent_card.name] = agent_card
        print(f"Registered agent: {agent_card.name}")
    
    def discover_agent_capabilities(self, agent_endpoint: str) -> Optional[AgentCard]:
        """Discover capabilities of a remote agent via A2A"""
        message = A2AMessage(
            method="get_capabilities",
            params={},
            id=f"discover_{int(time.time())}"
        )
        
        try:
            response = requests.post(
                f"{agent_endpoint}/a2a",
                json=message.__dict__,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return AgentCard(**result["result"])
        except Exception as e:
            print(f"Discovery failed for {agent_endpoint}: {e}")
        
        return None
    
    def delegate_task(self, agent_name: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate a task to a specialized agent using A2A protocol"""
        if agent_name not in self.known_agents:
            return {"error": f"Unknown agent: {agent_name}"}
        
        agent = self.known_agents[agent_name]
        task_id = f"task_{int(time.time())}"
        
        message = A2AMessage(
            method="execute_task",
            params={
                "task_id": task_id,
                "task_type": task_data.get("type", "generic"),
                "data": task_data.get("data", {}),
                "context": {
                    "requester": self.name,
                    "priority": task_data.get("priority", "medium")
                }
            },
            id=task_id
        )
        
        try:
            response = requests.post(
                f"{agent.endpoint}/a2a",
                json=message.__dict__,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.tasks[task_id] = {
                    "status": TaskStatus.IN_PROGRESS,
                    "agent": agent_name,
                    "created_at": time.time()
                }
                return result
            else:
                return {"error": f"Task delegation failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Communication error: {e}"}
    
    def coordinate_complex_task(self, task_description: str) -> Dict[str, Any]:
        """Coordinate a complex task across multiple agents"""
        print(f"Coordinating task: {task_description}")
        
        # Example: Process sales data
        if "sales data" in task_description.lower():
            # Step 1: Delegate data processing to DataProcessor agent
            processing_result = self.delegate_task("DataProcessor", {
                "type": "data_analysis",
                "data": {
                    "dataset": "sales_q4_2024.csv",
                    "operations": ["clean", "aggregate", "trend_analysis"]
                },
                "priority": "high"
            })
            
            if "error" in processing_result:
                return processing_result
            
            # Step 2: Wait for processing completion (in real implementation, use async)
            time.sleep(2)
            
            # Step 3: Aggregate results
            return {
                "task_id": f"coord_{int(time.time())}",
                "status": "completed",
                "result": {
                    "description": task_description,
                    "delegated_tasks": [processing_result],
                    "coordination_summary": "Successfully coordinated sales data analysis"
                }
            }
        
        return {"error": "Unknown task type"}
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Return this agent's capability card"""
        return {
            "name": self.agent_card.name,
            "description": self.agent_card.description,
            "capabilities": self.agent_card.capabilities,
            "endpoint": self.agent_card.endpoint,
            "version": self.agent_card.version
        }

if __name__ == "__main__":
    # Initialize coordinator agent
    coordinator = TaskCoordinatorAgent("TaskCoordinator")
    
    # Example agent card for a data processor
    data_agent_card = AgentCard(
        name="DataProcessor",
        description="Specialized agent for data processing and analysis",
        capabilities=["data_cleaning", "statistical_analysis", "trend_detection"],
        endpoint="http://localhost:8002"
    )
    
    coordinator.register_agent(data_agent_card)
    
    # Demonstrate capability
    print("Agent Card:", json.dumps(coordinator.get_agent_card(), indent=2))
    
    # Example task coordination
    result = coordinator.coordinate_complex_task("Analyze Q4 sales data for trends")
    print("Task Result:", json.dumps(result, indent=2))