"""
Client Data Agent - Provides client portfolio and holdings data
Specialized agent for retrieving client information and portfolio holdings
"""

import json
import time
import random
import pandas as pd
import os
from typing import Dict, Any
from flask import Flask, request, jsonify
from dataclasses import dataclass

@dataclass
class A2AMessage:
    """A2A Protocol Message Structure"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = None
    id: str = ""

class ClientDataAgent:
    """Agent specializing in client data and portfolio holdings"""
    
    def __init__(self, name: str = "ClientDataAgent", port: int = 8003):
        self.name = name
        self.port = port
        self.endpoint = f"http://localhost:{port}"
        self.active_tasks = {}
        
        # Initialize Flask app for A2A communication
        self.app = Flask(__name__)
        self.setup_routes()
        
        # Load client portfolio data from CSV files
        self.client_portfolios = self.load_client_data()
    
    def load_client_data(self) -> Dict[str, Any]:
        """Load client data from CSV files"""
        try:
            # Load clients info
            clients_df = pd.read_csv('data/clients.csv')
            holdings_df = pd.read_csv('data/client_holdings.csv')
            
            portfolios = {}
            
            for _, client_row in clients_df.iterrows():
                client_id = client_row['client_id']
                
                # Get holdings for this client
                client_holdings = holdings_df[holdings_df['client_id'] == client_id]
                holdings_list = []
                
                for _, holding_row in client_holdings.iterrows():
                    holdings_list.append({
                        "symbol": holding_row['symbol'],
                        "shares": holding_row['shares'],
                        "avg_cost": holding_row['avg_cost']
                    })
                
                portfolios[client_id] = {
                    "name": client_row['client_name'],
                    "account_value": client_row['account_value'],
                    "holdings": holdings_list
                }
            
            return portfolios
            
        except Exception as e:
            print(f"Error loading client data from CSV: {e}")
            # Fallback to empty data if CSV files not found
            return {}
    
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
            "name": "ClientDataAgent",
            "description": "Provides client portfolio data, holdings, and account information",
            "capabilities": [
                "get_client_portfolio",
                "get_client_holdings",
                "get_all_client_data",
                "aggregate_holdings",
                "client_portfolio_summary"
            ],
            "endpoint": self.endpoint,
            "version": "1.0"
        }
    
    def execute_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a client data task"""
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
            if task_type == "get_client_portfolio":
                result = self.get_client_portfolio(data)
            elif task_type == "get_client_holdings":
                result = self.get_client_holdings(data)
            elif task_type == "get_all_client_data":
                result = self.get_all_client_data(data)
            elif task_type == "aggregate_holdings":
                result = self.aggregate_holdings(data)
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
    
    def get_client_portfolio(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific client portfolio data"""
        client_id = data.get("client_id", "CLIENT001")
        
        if client_id not in self.client_portfolios:
            return {"error": f"Client {client_id} not found"}
        
        portfolio = self.client_portfolios[client_id]
        return {
            "client_id": client_id,
            "client_name": portfolio["name"],
            "account_value": portfolio["account_value"],
            "holdings_count": len(portfolio["holdings"]),
            "holdings": portfolio["holdings"]
        }
    
    def get_client_holdings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get holdings for a specific client"""
        client_id = data.get("client_id", "CLIENT001")
        
        if client_id not in self.client_portfolios:
            return {"error": f"Client {client_id} not found"}
        
        return {
            "client_id": client_id,
            "holdings": self.client_portfolios[client_id]["holdings"]
        }
    
    def get_all_client_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for all clients"""
        return {
            "total_clients": len(self.client_portfolios),
            "clients": {
                client_id: {
                    "name": portfolio["name"],
                    "account_value": portfolio["account_value"],
                    "holdings": portfolio["holdings"]
                }
                for client_id, portfolio in self.client_portfolios.items()
            }
        }
    
    def aggregate_holdings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate holdings across all clients"""
        aggregated = {}
        total_portfolio_value = 0
        
        for client_id, portfolio in self.client_portfolios.items():
            total_portfolio_value += portfolio["account_value"]
            
            for holding in portfolio["holdings"]:
                symbol = holding["symbol"]
                shares = holding["shares"]
                avg_cost = holding["avg_cost"]
                
                if symbol not in aggregated:
                    aggregated[symbol] = {
                        "total_shares": 0,
                        "total_cost_basis": 0,
                        "client_count": 0,
                        "clients": []
                    }
                
                aggregated[symbol]["total_shares"] += shares
                aggregated[symbol]["total_cost_basis"] += shares * avg_cost
                aggregated[symbol]["client_count"] += 1
                aggregated[symbol]["clients"].append({
                    "client_id": client_id,
                    "shares": shares,
                    "avg_cost": avg_cost
                })
        
        # Calculate average cost for each symbol
        for symbol in aggregated:
            total_shares = aggregated[symbol]["total_shares"]
            total_cost = aggregated[symbol]["total_cost_basis"]
            aggregated[symbol]["avg_cost"] = total_cost / total_shares if total_shares > 0 else 0
        
        return {
            "total_portfolio_value": total_portfolio_value,
            "unique_symbols": len(aggregated),
            "aggregated_holdings": aggregated
        }
    
    def start_server(self):
        """Start the A2A protocol server"""
        print(f"Starting ClientData agent on port {self.port}")
        print(f"Agent Card: {json.dumps(self.get_agent_card(), indent=2)}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

if __name__ == "__main__":
    agent = ClientDataAgent()
    agent.start_server()