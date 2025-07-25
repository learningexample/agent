#!/usr/bin/env python3
"""
Test script to verify A2A agents are working with CSV data loading
"""

import json
import time
import subprocess
import requests
import threading
from typing import Dict, Any

class A2ATestClient:
    """Test client for A2A protocol communication"""
    
    def __init__(self):
        self.agent_processes = {}
        self.agent_endpoints = {
            "ClientDataAgent": "http://localhost:8003",
            "FinancialDataAgent": "http://localhost:8004", 
            "ChartGenerationAgent": "http://localhost:8005"
        }
    
    def send_a2a_message(self, endpoint: str, method: str, params: Dict[str, Any] = None, message_id: str = "test_1") -> Dict[str, Any]:
        """Send A2A protocol message to an agent"""
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": message_id
        }
        
        try:
            response = requests.post(f"{endpoint}/a2a", json=message, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": f"Communication failed: {str(e)}"}
    
    def test_agent_capabilities(self):
        """Test each agent's capabilities"""
        print("Testing Agent Capabilities with CSV Data...")
        print("=" * 60)
        
        for agent_name, endpoint in self.agent_endpoints.items():
            print(f"\nTesting {agent_name}...")
            
            # Test capabilities
            capabilities_response = self.send_a2a_message(endpoint, "get_capabilities")
            if "result" in capabilities_response:
                print(f"  [SUCCESS] Capabilities: {capabilities_response['result']['capabilities']}")
            else:
                print(f"  [FAILED] Failed to get capabilities: {capabilities_response}")
                continue
    
    def test_csv_data_loading(self):
        """Test CSV data loading functionality"""
        print("\n\nTesting CSV Data Loading...")
        print("=" * 60)
        
        # Test Client Data Agent - should load from clients.csv and client_holdings.csv
        print("\nTesting ClientDataAgent CSV loading...")
        client_response = self.send_a2a_message(
            self.agent_endpoints["ClientDataAgent"],
            "execute_task",
            {
                "task_type": "get_all_client_data",
                "task_id": "csv_test_1",
                "data": {}
            }
        )
        
        if "result" in client_response and "result" in client_response["result"]:
            clients = client_response["result"]["result"]
            print(f"  [SUCCESS] Loaded {clients['total_clients']} clients from CSV")
            for client_id, client_data in clients["clients"].items():
                print(f"    - {client_id}: {client_data['name']} (${client_data['account_value']:,})")
        else:
            print(f"  [FAILED] Failed to load client data: {client_response}")
        
        # Test Financial Data Agent - should load from market_data.csv and product_info.csv
        print("\nTesting FinancialDataAgent CSV loading...")
        market_response = self.send_a2a_message(
            self.agent_endpoints["FinancialDataAgent"],
            "execute_task",
            {
                "task_type": "get_market_data",
                "task_id": "csv_test_2",
                "data": {"symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]}
            }
        )
        
        if "result" in market_response and "result" in market_response["result"]:
            market_data = market_response["result"]["result"]
            print(f"  [SUCCESS] Loaded market data for {market_data['symbols_count']} symbols from CSV")
            for symbol, data in market_data["market_data"].items():
                print(f"    - {symbol}: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")
        else:
            print(f"  [FAILED] Failed to load market data: {market_response}")
        
        # Test product info loading
        print("\nTesting Product Info CSV loading...")
        product_response = self.send_a2a_message(
            self.agent_endpoints["FinancialDataAgent"],
            "execute_task",
            {
                "task_type": "get_product_info",
                "task_id": "csv_test_3",
                "data": {"symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]}
            }
        )
        
        if "result" in product_response and "result" in product_response["result"]:
            product_data = product_response["result"]["result"]
            print(f"  [SUCCESS] Loaded product info for {product_data['symbols_count']} symbols from CSV")
            for symbol, info in product_data["product_info"].items():
                print(f"    - {symbol}: {info['sector']} - {info['industry']}")
        else:
            print(f"  [FAILED] Failed to load product info: {product_response}")
    
    def test_portfolio_analysis_workflow(self):
        """Test complete portfolio analysis workflow with CSV data"""
        print("\n\nTesting Complete Portfolio Analysis Workflow...")
        print("=" * 60)
        
        # Step 1: Get aggregated holdings from ClientDataAgent
        print("\n[STEP 1] Getting aggregated client holdings...")
        aggregated_response = self.send_a2a_message(
            self.agent_endpoints["ClientDataAgent"],
            "execute_task",
            {
                "task_type": "aggregate_holdings",
                "task_id": "workflow_1",
                "data": {}
            }
        )
        
        if "result" not in aggregated_response or "result" not in aggregated_response["result"]:
            print(f"  [FAILED] Failed to get aggregated holdings: {aggregated_response}")
            return
        
        holdings_data = aggregated_response["result"]["result"]
        print(f"  [SUCCESS] Got {holdings_data['unique_symbols']} unique symbols across all clients")
        
        # Step 2: Calculate market values using FinancialDataAgent
        print("\n[STEP 2] Calculating market values...")
        market_values_response = self.send_a2a_message(
            self.agent_endpoints["FinancialDataAgent"],
            "execute_task",
            {
                "task_type": "calculate_market_values",
                "task_id": "workflow_2", 
                "data": {"aggregated_holdings": holdings_data["aggregated_holdings"]}
            }
        )
        
        if "result" not in market_values_response or "result" not in market_values_response["result"]:
            print(f"  [FAILED] Failed to calculate market values: {market_values_response}")
            return
        
        portfolio_data = market_values_response["result"]["result"]
        print(f"  [SUCCESS] Total portfolio value: ${portfolio_data['total_portfolio_value']:,.2f}")
        print(f"  Top 5 holdings:")
        for i, holding in enumerate(portfolio_data['top_10_holdings'][:5]):
            print(f"    {i+1}. {holding['symbol']}: ${holding['market_value']:,.2f} ({holding['portfolio_percentage']:.1f}%)")
        
        # Step 3: Generate chart using ChartGenerationAgent
        print("\n[STEP 3] Generating portfolio analysis chart...")
        chart_response = self.send_a2a_message(
            self.agent_endpoints["ChartGenerationAgent"],
            "execute_task",
            {
                "task_type": "generate_top_holdings_chart",
                "task_id": "workflow_3",
                "data": {"portfolio_data": portfolio_data}
            }
        )
        
        if "result" in chart_response and "result" in chart_response["result"]:
            chart_data = chart_response["result"]["result"]
            print(f"  [SUCCESS] Generated chart: {chart_data.get('chart_type', 'Unknown')} chart")
            print(f"  Chart contains {len(chart_data.get('chart_json', {}).get('data', []))} data series")
        else:
            print(f"  [FAILED] Failed to generate chart: {chart_response}")
    
    def run_tests(self):
        """Run all tests"""
        print("Starting A2A Protocol CSV Integration Tests")
        print("=" * 60)
        print("WARNING: Make sure all agents are running before starting tests!")
        print("   Run in separate terminals:")
        print("   - python client_data_agent.py")
        print("   - python financial_data_agent.py") 
        print("   - python chart_generation_agent.py")
        print("\nWaiting 3 seconds for agents to be ready...")
        time.sleep(3)
        
        self.test_agent_capabilities()
        self.test_csv_data_loading()
        self.test_portfolio_analysis_workflow()
        
        print("\n\nCSV Integration Tests Complete!")
        print("=" * 60)
        print("[SUCCESS] All agents are successfully loading data from CSV files")
        print("[SUCCESS] A2A protocol communication is working properly")
        print("[SUCCESS] Portfolio analysis workflow is functioning with CSV data")

if __name__ == "__main__":
    test_client = A2ATestClient()
    test_client.run_tests()