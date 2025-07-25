"""
Web UI for Google Agent2Agent Protocol Demo
Interactive dashboard to visualize agent communication
"""

from flask import Flask, render_template, jsonify, request
import json
import time
import threading
import requests
import concurrent.futures
from datetime import datetime
from a2a_protocol import A2AProtocolClient

app = Flask(__name__)

class A2AWebUI:
    """Web interface for A2A protocol demonstration"""
    
    def __init__(self):
        self.client = A2AProtocolClient()
        self.message_log = []
        self.agent_status = {}
        self.known_agents = {
            "DataProcessor": "http://localhost:8002",
            "ClientDataAgent": "http://localhost:8003",
            "FinancialDataAgent": "http://localhost:8004",
            "ChartGenerationAgent": "http://localhost:8005"
        }
        
    def log_message(self, direction, agent, message, response=None):
        """Log A2A protocol messages for display"""
        log_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "direction": direction,  # "sent" or "received"
            "agent": agent,
            "message": message,
            "response": response,
            "id": len(self.message_log) + 1
        }
        self.message_log.append(log_entry)
        
        # Keep only last 50 messages
        if len(self.message_log) > 50:
            self.message_log = self.message_log[-50:]
    
    def check_agent_status(self, agent_name, endpoint):
        """Check if an agent is online"""
        try:
            response = requests.get(f"{endpoint}/health", timeout=1)
            return agent_name, {
                "online": response.status_code == 200,
                "last_check": datetime.now().strftime("%H:%M:%S")
            }
        except:
            return agent_name, {
                "online": False,
                "last_check": datetime.now().strftime("%H:%M:%S")
            }
    
    def check_all_agents_status(self):
        """Check status of all agents concurrently"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all health checks simultaneously
            future_to_agent = {
                executor.submit(self.check_agent_status, name, endpoint): name 
                for name, endpoint in self.known_agents.items()
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_agent):
                agent_name, status = future.result()
                self.agent_status[agent_name] = status
    
    def discover_capabilities(self, agent_name):
        """Discover agent capabilities and log the interaction"""
        if agent_name not in self.known_agents:
            return {"error": "Unknown agent"}
        
        endpoint = self.known_agents[agent_name]
        
        # Log outgoing message
        self.log_message("sent", agent_name, {
            "method": "get_capabilities",
            "purpose": "Capability discovery"
        })
        
        capabilities = self.client.discover_capabilities(endpoint)
        
        # Log response
        if capabilities:
            self.log_message("received", agent_name, "Capabilities discovered", {
                "name": capabilities.name,
                "capabilities": [cap.name for cap in capabilities.capabilities]
            })
            return {
                "name": capabilities.name,
                "description": capabilities.description,
                "capabilities": [cap.name for cap in capabilities.capabilities],
                "endpoint": capabilities.endpoint
            }
        else:
            self.log_message("received", agent_name, "Discovery failed", {"error": "No response"})
            return {"error": "Discovery failed"}
    
    def send_task(self, agent_name, task_type, task_data):
        """Send task to agent and log the interaction"""
        if agent_name not in self.known_agents:
            return {"error": "Unknown agent"}
        
        endpoint = self.known_agents[agent_name]
        task_id = f"web_task_{int(time.time())}"
        
        task_params = {
            "task_id": task_id,
            "task_type": task_type,
            "data": task_data,
            "context": {
                "requester": "WebUI",
                "priority": "medium"
            }
        }
        
        # Log outgoing message
        self.log_message("sent", agent_name, {
            "method": "execute_task",
            "task_type": task_type,
            "task_id": task_id
        })
        
        response = self.client.send_task(endpoint, "execute_task", task_params)
        
        # Log response
        if "error" not in response:
            result = response.get("result", {})
            self.log_message("received", agent_name, "Task completed", {
                "status": result.get("status"),
                "processing_time": result.get("processing_time", 0)
            })
        else:
            self.log_message("received", agent_name, "Task failed", response.get("error"))
        
        return response

# Initialize the web UI controller
ui_controller = A2AWebUI()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/agents/status')
def get_agent_status():
    """Get status of all known agents"""
    ui_controller.check_all_agents_status()
    return jsonify(ui_controller.agent_status)

@app.route('/api/agents/<agent_name>/capabilities')
def get_agent_capabilities(agent_name):
    """Discover agent capabilities"""
    result = ui_controller.discover_capabilities(agent_name)
    return jsonify(result)

@app.route('/api/agents/<agent_name>/task', methods=['POST'])
def send_agent_task(agent_name):
    """Send task to specific agent"""
    data = request.get_json()
    task_type = data.get('task_type', 'data_analysis')
    task_data = data.get('task_data', {})
    
    result = ui_controller.send_task(agent_name, task_type, task_data)
    return jsonify(result)

@app.route('/api/messages')
def get_message_log():
    """Get recent A2A protocol messages"""
    return jsonify(ui_controller.message_log)

@app.route('/api/messages/clear', methods=['POST'])
def clear_message_log():
    """Clear all A2A protocol messages"""
    ui_controller.message_log.clear()
    return jsonify({"status": "success", "message": "Message log cleared"})

@app.route('/api/charts/<chart_type>')
def generate_chart(chart_type):
    """Generate specific chart types"""
    try:
        # Get sample data for chart generation
        if chart_type == "top_holdings":
            # Get client data
            client_result = ui_controller.send_task("ClientDataAgent", "aggregate_holdings", {})
            if "error" in client_result:
                return jsonify({"error": "Failed to get client data"}), 500
            
            # Get market data
            aggregated = client_result["result"]["result"]["aggregated_holdings"]
            market_result = ui_controller.send_task("FinancialDataAgent", "calculate_market_values", {
                "aggregated_holdings": aggregated
            })
            if "error" in market_result:
                return jsonify({"error": "Failed to get market data"}), 500
            
            # Generate chart
            holdings = market_result["result"]["result"]["holdings"]
            chart_result = ui_controller.send_task("ChartGenerationAgent", "generate_top_holdings_chart", {
                "holdings": holdings,
                "title": "Top 10 Client Holdings"
            })
            
            return jsonify(chart_result)
        
        elif chart_type == "pie_chart":
            # Similar workflow for pie chart
            client_result = ui_controller.send_task("ClientDataAgent", "aggregate_holdings", {})
            if "error" in client_result:
                return jsonify({"error": "Failed to get client data"}), 500
            
            aggregated = client_result["result"]["result"]["aggregated_holdings"]
            market_result = ui_controller.send_task("FinancialDataAgent", "calculate_market_values", {
                "aggregated_holdings": aggregated
            })
            if "error" in market_result:
                return jsonify({"error": "Failed to get market data"}), 500
            
            holdings = market_result["result"]["result"]["holdings"]
            chart_result = ui_controller.send_task("ChartGenerationAgent", "generate_portfolio_pie_chart", {
                "holdings": holdings,
                "title": "Portfolio Allocation"
            })
            
            return jsonify(chart_result)
        
        else:
            return jsonify({"error": "Unknown chart type"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/demo/run/<demo_type>')
def run_demo(demo_type):
    """Run predefined demo scenarios"""
    if demo_type == "capability_discovery":
        results = {}
        for agent_name in ui_controller.known_agents.keys():
            results[agent_name] = ui_controller.discover_capabilities(agent_name)
        return jsonify({"demo": "capability_discovery", "results": results})
    
    elif demo_type == "portfolio_analysis":
        # Complete portfolio analysis workflow
        results = []
        
        # Step 1: Get client data
        client_result = ui_controller.send_task("ClientDataAgent", "aggregate_holdings", {})
        results.append({"step": "client_data", "result": client_result})
        
        if "error" not in client_result and "result" in client_result:
            aggregated = client_result["result"]["result"]["aggregated_holdings"]
            
            # Step 2: Get market data
            market_result = ui_controller.send_task("FinancialDataAgent", "calculate_market_values", {
                "aggregated_holdings": aggregated
            })
            results.append({"step": "market_data", "result": market_result})
            
            if "error" not in market_result and "result" in market_result:
                holdings = market_result["result"]["result"]["holdings"]
                
                # Step 3: Generate chart
                chart_result = ui_controller.send_task("ChartGenerationAgent", "generate_top_holdings_chart", {
                    "holdings": holdings,
                    "title": "Top 10 Client Holdings Portfolio"
                })
                results.append({"step": "chart_generation", "result": chart_result})
        
        return jsonify({"demo": "portfolio_analysis", "results": results})
    
    elif demo_type == "data_analysis":
        task_data = {
            "dataset": "sample_sales_data.csv",
            "operations": ["clean", "aggregate", "trend_analysis"]
        }
        result = ui_controller.send_task("DataProcessor", "data_analysis", task_data)
        return jsonify({"demo": "data_analysis", "result": result})
    
    elif demo_type == "workflow":
        # Multi-step workflow
        results = []
        
        # Step 1: Data cleaning
        result1 = ui_controller.send_task("DataProcessor", "data_cleaning", {"dataset": "raw_data.csv"})
        results.append(result1)
        
        # Step 2: Analysis
        result2 = ui_controller.send_task("DataProcessor", "data_analysis", {"dataset": "cleaned_data.csv"})
        results.append(result2)
        
        return jsonify({"demo": "workflow", "results": results})
    
    else:
        return jsonify({"error": "Unknown demo type"}), 400

if __name__ == '__main__':
    print("Starting A2A Protocol Web UI...")
    print("Dashboard available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)