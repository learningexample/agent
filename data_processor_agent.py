"""
Google Agent2Agent Protocol Example - Data Processor Agent
This agent specializes in data processing and analysis tasks.
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any
from dataclasses import dataclass
from flask import Flask, request, jsonify
import threading
import time

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

class DataProcessorAgent:
    """Specialized agent for data processing using A2A protocol"""
    
    def __init__(self, name: str = "DataProcessor", port: int = 8002):
        self.name = name
        self.port = port
        self.endpoint = f"http://localhost:{port}"
        self.active_tasks = {}
        
        # Agent card for capability discovery
        self.agent_card = AgentCard(
            name="DataProcessor",
            description="Specialized agent for data processing, cleaning, and analysis",
            capabilities=[
                "data_cleaning",
                "statistical_analysis", 
                "trend_detection",
                "data_aggregation",
                "csv_processing",
                "json_processing"
            ],
            endpoint=self.endpoint
        )
        
        # Initialize Flask app for A2A communication
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup A2A protocol endpoints"""
        
        @self.app.route('/a2a', methods=['POST'])
        def handle_a2a_message():
            """Handle incoming A2A protocol messages"""
            try:
                message_data = request.get_json()
                message = A2AMessage(**message_data)
                
                if message.method == "get_capabilities":
                    return jsonify({
                        "jsonrpc": "2.0",
                        "result": self.get_agent_card(),
                        "id": message.id
                    })
                
                elif message.method == "execute_task":
                    result = self.execute_task(message.params)
                    return jsonify({
                        "jsonrpc": "2.0",
                        "result": result,
                        "id": message.id
                    })
                
                else:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": "Method not found"},
                        "id": message.id
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                    "id": getattr(message, 'id', None)
                }), 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy", "agent": self.name})
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Return this agent's capability card"""
        return {
            "name": self.agent_card.name,
            "description": self.agent_card.description,
            "capabilities": self.agent_card.capabilities,
            "endpoint": self.agent_card.endpoint,
            "version": self.agent_card.version
        }
    
    def execute_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data processing task"""
        task_id = params.get("task_id", f"task_{int(time.time())}")
        task_type = params.get("task_type", "generic")
        data = params.get("data", {})
        context = params.get("context", {})
        
        print(f"Executing task {task_id} of type {task_type}")
        
        # Store task in active tasks
        self.active_tasks[task_id] = {
            "status": "in_progress",
            "started_at": time.time(),
            "requester": context.get("requester", "unknown")
        }
        
        try:
            if task_type == "data_analysis":
                result = self.analyze_data(data)
            elif task_type == "data_cleaning":
                result = self.clean_data(data)
            elif task_type == "trend_analysis":
                result = self.detect_trends(data)
            else:
                result = {"error": f"Unsupported task type: {task_type}"}
            
            # Update task status
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["completed_at"] = time.time()
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "agent": self.name,
                "processing_time": time.time() - self.active_tasks[task_id]["started_at"]
            }
            
        except Exception as e:
            self.active_tasks[task_id]["status"] = "failed"
            self.active_tasks[task_id]["error"] = str(e)
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "agent": self.name
            }
    
    def analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive data analysis"""
        dataset = data.get("dataset", "sample_data")
        operations = data.get("operations", ["basic_stats"])
        
        # Simulate data loading and processing
        print(f"Processing dataset: {dataset}")
        
        # Generate sample data for demonstration
        sample_data = np.random.normal(100, 15, 1000)
        df = pd.DataFrame({
            'sales': sample_data,
            'month': np.repeat(['Jan', 'Feb', 'Mar', 'Apr'], 250)
        })
        
        results = {}
        
        for operation in operations:
            if operation == "clean":
                # Data cleaning simulation
                cleaned_rows = len(df) - 10  # Simulate removing 10 bad rows
                results["cleaning"] = {
                    "original_rows": len(df),
                    "cleaned_rows": cleaned_rows,
                    "removed_rows": 10
                }
            
            elif operation == "aggregate":
                # Data aggregation
                monthly_stats = df.groupby('month')['sales'].agg(['mean', 'sum', 'count']).to_dict()
                results["aggregation"] = {
                    "monthly_averages": monthly_stats['mean'],
                    "monthly_totals": monthly_stats['sum'],
                    "monthly_counts": monthly_stats['count']
                }
            
            elif operation == "trend_analysis":
                # Trend detection
                monthly_means = df.groupby('month')['sales'].mean()
                trend = "increasing" if monthly_means.iloc[-1] > monthly_means.iloc[0] else "decreasing"
                results["trends"] = {
                    "overall_trend": trend,
                    "monthly_progression": monthly_means.to_dict(),
                    "variance": df['sales'].var()
                }
        
        return {
            "dataset_info": {
                "name": dataset,
                "rows": len(df),
                "columns": list(df.columns)
            },
            "analysis_results": results,
            "summary": "Data analysis completed successfully"
        }
    
    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and preprocess data"""
        return {
            "operation": "data_cleaning",
            "cleaned_records": 950,
            "removed_duplicates": 25,
            "filled_missing_values": 15,
            "status": "completed"
        }
    
    def detect_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect trends in data"""
        return {
            "operation": "trend_detection",
            "trends_found": [
                {"metric": "sales", "trend": "upward", "confidence": 0.85},
                {"metric": "customer_satisfaction", "trend": "stable", "confidence": 0.92}
            ],
            "anomalies": 3,
            "status": "completed"
        }
    
    def start_server(self):
        """Start the A2A protocol server"""
        print(f"Starting DataProcessor agent on port {self.port}")
        print(f"Agent Card: {json.dumps(self.get_agent_card(), indent=2)}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

if __name__ == "__main__":
    agent = DataProcessorAgent()
    agent.start_server()