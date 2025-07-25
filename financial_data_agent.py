"""
Financial Product Data Agent - Provides real-time market data and financial product information
Specialized agent for retrieving stock prices, market data, and financial product details
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

class FinancialDataAgent:
    """Agent specializing in financial market data and product information"""
    
    def __init__(self, name: str = "FinancialDataAgent", port: int = 8004):
        self.name = name
        self.port = port
        self.endpoint = f"http://localhost:{port}"
        self.active_tasks = {}
        
        # Initialize Flask app for A2A communication
        self.app = Flask(__name__)
        self.setup_routes()
        
        # Load market data and product info from CSV files
        self.market_data, self.product_info = self.load_market_data()
    
    def load_market_data(self) -> tuple[Dict[str, Dict], Dict[str, Dict]]:
        """Load market data and product info from CSV files"""
        try:
            # Load market data
            market_df = pd.read_csv('data/market_data.csv')
            product_df = pd.read_csv('data/product_info.csv')
            
            market_data = {}
            product_info = {}
            
            # Process market data
            for _, row in market_df.iterrows():
                symbol = row['symbol']
                market_data[symbol] = {
                    "price": row['price'],
                    "change": row['change'],
                    "change_pct": row['change_pct'],
                    "volume": row['volume'],
                    "market_cap": row['market_cap'] if pd.notna(row['market_cap']) else None
                }
            
            # Process product info
            for _, row in product_df.iterrows():
                symbol = row['symbol']
                product_info[symbol] = {
                    "sector": row['sector'],
                    "industry": row['industry'],
                    "category": row['category']
                }
            
            print(f"Loaded market data for {len(market_data)} symbols from CSV")
            print(f"Loaded product info for {len(product_info)} symbols from CSV")
            
            return market_data, product_info
            
        except Exception as e:
            print(f"Error loading data from CSV: {e}")
            # Fallback to hardcoded data
            return self.get_fallback_data()
    
    def get_fallback_data(self) -> tuple[Dict[str, Dict], Dict[str, Dict]]:
        """Return fallback hardcoded data if CSV loading fails"""
        market_data = {
            "AAPL": {"price": 185.25, "change": 2.15, "change_pct": 1.17, "volume": 45231000, "market_cap": 2.85e12},
            "MSFT": {"price": 378.50, "change": -1.25, "change_pct": -0.33, "volume": 32145000, "market_cap": 2.81e12},
            "GOOGL": {"price": 2785.40, "change": 15.30, "change_pct": 0.55, "volume": 28942000, "market_cap": 1.75e12},
        }
        
        product_info = {
            "AAPL": {"sector": "Technology", "industry": "Consumer Electronics", "category": "Large Cap Growth"},
            "MSFT": {"sector": "Technology", "industry": "Software", "category": "Large Cap Growth"},
            "GOOGL": {"sector": "Technology", "industry": "Internet Services", "category": "Large Cap Growth"},
        }
        
        return market_data, product_info
    
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
            "name": "FinancialDataAgent",
            "description": "Provides real-time market data, stock prices, and financial product information",
            "capabilities": [
                "get_stock_price",
                "get_market_data",
                "get_portfolio_values",
                "get_product_info",
                "calculate_market_values"
            ],
            "endpoint": self.endpoint,
            "version": "1.0"
        }
    
    def execute_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a financial data task"""
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
            if task_type == "get_stock_price":
                result = self.get_stock_price(data)
            elif task_type == "get_market_data":
                result = self.get_market_data(data)
            elif task_type == "get_portfolio_values":
                result = self.get_portfolio_values(data)
            elif task_type == "get_product_info":
                result = self.get_product_info(data)
            elif task_type == "calculate_market_values":
                result = self.calculate_market_values(data)
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
    
    def get_stock_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current stock price for a symbol"""
        symbol = data.get("symbol", "AAPL").upper()
        
        if symbol not in self.market_data:
            return {"error": f"Symbol {symbol} not found"}
        
        # Add small random fluctuation to simulate real-time data
        base_price = self.market_data[symbol]["price"]
        fluctuation = random.uniform(-0.02, 0.02)  # ±2% fluctuation
        current_price = base_price * (1 + fluctuation)
        
        return {
            "symbol": symbol,
            "price": round(current_price, 2),
            "base_price": base_price,
            "change": self.market_data[symbol]["change"],
            "change_pct": self.market_data[symbol]["change_pct"],
            "volume": self.market_data[symbol]["volume"],
            "timestamp": time.time()
        }
    
    def get_market_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get market data for multiple symbols"""
        symbols = data.get("symbols", list(self.market_data.keys()))
        
        market_data = {}
        for symbol in symbols:
            if symbol.upper() in self.market_data:
                symbol_upper = symbol.upper()
                base_price = self.market_data[symbol_upper]["price"]
                fluctuation = random.uniform(-0.02, 0.02)
                current_price = base_price * (1 + fluctuation)
                
                market_data[symbol_upper] = {
                    "price": round(current_price, 2),
                    "change": self.market_data[symbol_upper]["change"],
                    "change_pct": self.market_data[symbol_upper]["change_pct"],
                    "volume": self.market_data[symbol_upper]["volume"],
                    "market_cap": self.market_data[symbol_upper]["market_cap"]
                }
        
        return {
            "timestamp": time.time(),
            "symbols_count": len(market_data),
            "market_data": market_data
        }
    
    def get_portfolio_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate portfolio values based on holdings"""
        holdings = data.get("holdings", [])
        
        portfolio_values = []
        total_market_value = 0
        
        for holding in holdings:
            symbol = holding.get("symbol", "").upper()
            shares = holding.get("shares", 0)
            
            if symbol in self.market_data:
                base_price = self.market_data[symbol]["price"]
                fluctuation = random.uniform(-0.02, 0.02)
                current_price = base_price * (1 + fluctuation)
                market_value = shares * current_price
                total_market_value += market_value
                
                portfolio_values.append({
                    "symbol": symbol,
                    "shares": shares,
                    "current_price": round(current_price, 2),
                    "market_value": round(market_value, 2),
                    "avg_cost": holding.get("avg_cost", 0),
                    "cost_basis": shares * holding.get("avg_cost", 0),
                    "unrealized_gain_loss": round(market_value - (shares * holding.get("avg_cost", 0)), 2)
                })
        
        # Calculate portfolio percentages
        for holding in portfolio_values:
            holding["portfolio_percentage"] = round((holding["market_value"] / total_market_value * 100), 2) if total_market_value > 0 else 0
        
        return {
            "total_market_value": round(total_market_value, 2),
            "holdings_count": len(portfolio_values),
            "holdings": portfolio_values,
            "timestamp": time.time()
        }
    
    def get_product_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get product information for symbols"""
        symbols = data.get("symbols", [])
        
        product_info = {}
        for symbol in symbols:
            symbol_upper = symbol.upper()
            if symbol_upper in self.product_info:
                product_info[symbol_upper] = self.product_info[symbol_upper]
        
        return {
            "symbols_count": len(product_info),
            "product_info": product_info
        }
    
    def calculate_market_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate market values for aggregated holdings"""
        aggregated_holdings = data.get("aggregated_holdings", {})
        
        market_values = {}
        total_portfolio_value = 0
        
        for symbol, holding_data in aggregated_holdings.items():
            if symbol in self.market_data:
                shares = holding_data.get("total_shares", 0)
                base_price = self.market_data[symbol]["price"]
                fluctuation = random.uniform(-0.02, 0.02)
                current_price = base_price * (1 + fluctuation)
                market_value = shares * current_price
                total_portfolio_value += market_value
                
                market_values[symbol] = {
                    "symbol": symbol,
                    "total_shares": shares,
                    "current_price": round(current_price, 2),
                    "market_value": round(market_value, 2),
                    "avg_cost": holding_data.get("avg_cost", 0),
                    "cost_basis": round(holding_data.get("total_cost_basis", 0), 2),
                    "unrealized_gain_loss": round(market_value - holding_data.get("total_cost_basis", 0), 2),
                    "client_count": holding_data.get("client_count", 0),
                    "sector": self.product_info.get(symbol, {}).get("sector", "Unknown"),
                    "industry": self.product_info.get(symbol, {}).get("industry", "Unknown")
                }
        
        # Calculate percentages and sort by market value
        sorted_holdings = []
        for symbol, data in market_values.items():
            data["portfolio_percentage"] = round((data["market_value"] / total_portfolio_value * 100), 2) if total_portfolio_value > 0 else 0
            sorted_holdings.append(data)
        
        # Sort by market value descending
        sorted_holdings.sort(key=lambda x: x["market_value"], reverse=True)
        
        return {
            "total_portfolio_value": round(total_portfolio_value, 2),
            "unique_symbols": len(market_values),
            "holdings": sorted_holdings,
            "top_10_holdings": sorted_holdings[:10],
            "timestamp": time.time()
        }
    
    def start_server(self):
        """Start the A2A protocol server"""
        print(f"Starting FinancialData agent on port {self.port}")
        print(f"Agent Card: {json.dumps(self.get_agent_card(), indent=2)}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

if __name__ == "__main__":
    agent = FinancialDataAgent()
    agent.start_server()