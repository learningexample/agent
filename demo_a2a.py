"""
Google Agent2Agent Protocol Demonstration
Shows two agents communicating using the A2A protocol
"""

import json
import time
import threading
import subprocess
import sys
from typing import Dict, Any
from a2a_protocol import A2AProtocolClient, AgentCard, AgentCapability

class A2ADemo:
    """Demonstration of A2A protocol between agents"""
    
    def __init__(self):
        self.client = A2AProtocolClient()
        self.coordinator_endpoint = "http://localhost:8001"
        self.processor_endpoint = "http://localhost:8002"
        
    def wait_for_agent(self, endpoint: str, max_attempts: int = 10) -> bool:
        """Wait for agent to become available"""
        for attempt in range(max_attempts):
            try:
                response = self.client.session.get(f"{endpoint}/health", timeout=2)
                if response.status_code == 200:
                    print(f"Agent at {endpoint} is ready")
                    return True
            except:
                pass
            
            print(f"Waiting for agent at {endpoint}... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(1)
        
        return False
    
    def discover_agent_capabilities(self, endpoint: str) -> AgentCard:
        """Discover and display agent capabilities"""
        print(f"\nDiscovering capabilities for agent at {endpoint}")
        
        capabilities = self.client.discover_capabilities(endpoint)
        if capabilities:
            print(f"Agent Name: {capabilities.name}")
            print(f"Description: {capabilities.description}")
            print(f"Capabilities: {', '.join([cap.name for cap in capabilities.capabilities])}")
            print(f"Endpoint: {capabilities.endpoint}")
            return capabilities
        else:
            print(f"Failed to discover capabilities for {endpoint}")
            return None
    
    def demonstrate_task_delegation(self):
        """Demonstrate task delegation between agents"""
        print("\nDemonstrating Agent-to-Agent Task Delegation")
        print("=" * 60)
        
        # Task: Analyze quarterly sales data
        task_request = {
            "method": "execute_task",
            "params": {
                "task_id": f"demo_task_{int(time.time())}",
                "task_type": "data_analysis",
                "data": {
                    "dataset": "quarterly_sales_2024.csv",
                    "operations": ["clean", "aggregate", "trend_analysis"]
                },
                "context": {
                    "requester": "DemoCoordinator",
                    "priority": "high",
                    "deadline": "2024-12-31"
                }
            }
        }
        
        print(f"Sending task to DataProcessor agent...")
        print(f"Task: {task_request['params']['task_type']}")
        print(f"Dataset: {task_request['params']['data']['dataset']}")
        print(f"Operations: {task_request['params']['data']['operations']}")
        
        # Send task to data processor
        response = self.client.send_task(
            self.processor_endpoint,
            task_request["method"],
            task_request["params"]
        )
        
        print(f"\nResponse from DataProcessor:")
        if "error" in response:
            print(f"Error: {response['error']}")
        else:
            result = response.get("result", {})
            print(f"Task Status: {result.get('status', 'unknown')}")
            print(f"Task ID: {result.get('task_id', 'unknown')}")
            print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
            
            # Display analysis results
            if "result" in result and "analysis_results" in result["result"]:
                analysis = result["result"]["analysis_results"]
                print(f"\nAnalysis Results:")
                
                if "cleaning" in analysis:
                    cleaning = analysis["cleaning"]
                    print(f"  • Data Cleaning: {cleaning['cleaned_rows']} rows kept, {cleaning['removed_rows']} removed")
                
                if "aggregation" in analysis:
                    print(f"  • Monthly aggregation completed")
                
                if "trends" in analysis:
                    trends = analysis["trends"]
                    print(f"  • Trend Detection: {trends['overall_trend']} trend identified")
    
    def demonstrate_capability_negotiation(self):
        """Demonstrate capability discovery and negotiation"""
        print("\nDemonstrating Capability Discovery & Negotiation")
        print("=" * 60)
        
        # Discover processor capabilities
        processor_card = self.discover_agent_capabilities(self.processor_endpoint)
        
        if processor_card:
            # Check if processor can handle our required capabilities
            required_capabilities = ["data_cleaning", "statistical_analysis", "trend_detection"]
            available_capabilities = [cap.name for cap in processor_card.capabilities]
            
            print(f"\nCapability Matching:")
            for req_cap in required_capabilities:
                if req_cap in available_capabilities:
                    print(f"  + {req_cap}: Available")
                else:
                    print(f"  - {req_cap}: Not Available")
    
    def demonstrate_multi_agent_workflow(self):
        """Demonstrate complex workflow involving multiple agents"""
        print("\nDemonstrating Multi-Agent Workflow")
        print("=" * 60)
        
        # Simulate a complex business process
        workflow_steps = [
            {
                "step": 1,
                "description": "Data validation and cleaning",
                "agent": "DataProcessor",
                "task_type": "data_cleaning"
            },
            {
                "step": 2, 
                "description": "Statistical analysis",
                "agent": "DataProcessor",
                "task_type": "data_analysis"
            },
            {
                "step": 3,
                "description": "Trend detection and forecasting", 
                "agent": "DataProcessor",
                "task_type": "trend_analysis"
            }
        ]
        
        print("Executing workflow steps:")
        
        for step in workflow_steps:
            print(f"\nStep {step['step']}: {step['description']}")
            
            # Send task for this step
            task_params = {
                "task_id": f"workflow_step_{step['step']}_{int(time.time())}",
                "task_type": step["task_type"],
                "data": {
                    "dataset": "business_data.csv",
                    "step": step["step"]
                },
                "context": {
                    "workflow": "multi_agent_demo",
                    "step": step["step"]
                }
            }
            
            response = self.client.send_task(
                self.processor_endpoint,
                "execute_task", 
                task_params
            )
            
            if "error" not in response:
                result = response.get("result", {})
                print(f"  + Step {step['step']} completed in {result.get('processing_time', 0):.2f}s")
            else:
                print(f"  - Step {step['step']} failed: {response['error']}")
    
    def run_demo(self):
        """Run the complete A2A protocol demonstration"""
        print("Google Agent2Agent Protocol Demonstration")
        print("=" * 60)
        print("This demo shows two AI agents communicating using Google's A2A protocol:")
        print("• TaskCoordinator: Orchestrates complex tasks")  
        print("• DataProcessor: Specializes in data analysis")
        print()
        
        # Check if agents are running
        processor_ready = self.wait_for_agent(self.processor_endpoint)
        
        if not processor_ready:
            print("DataProcessor agent is not available. Please start it first:")
            print("   python data_processor_agent.py")
            return
        
        # Run demonstrations
        self.demonstrate_capability_negotiation()
        self.demonstrate_task_delegation()
        self.demonstrate_multi_agent_workflow()
        
        print("\nA2A Protocol Demonstration Complete!")
        print("\nKey A2A Protocol Features Demonstrated:")
        print("- Agent capability discovery")
        print("- JSON-RPC 2.0 message format")
        print("- Task delegation and coordination")
        print("- Multi-agent workflow orchestration")
        print("- Standardized error handling")
        print("- Secure agent-to-agent communication")

def main():
    """Main demonstration function"""
    demo = A2ADemo()
    
    try:
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")

if __name__ == "__main__":
    main()