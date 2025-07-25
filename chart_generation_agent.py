"""
Chart Generation Agent - Creates visualizations and charts from financial data
Specialized agent for generating portfolio analysis charts, graphs, and visual reports
"""

import json
import time
import base64
import io
from typing import Dict, Any
from flask import Flask, request, jsonify
from dataclasses import dataclass
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

@dataclass
class A2AMessage:
    """A2A Protocol Message Structure"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = None
    id: str = ""

class ChartGenerationAgent:
    """Agent specializing in chart and visualization generation"""
    
    def __init__(self, name: str = "ChartGenerationAgent", port: int = 8005):
        self.name = name
        self.port = port
        self.endpoint = f"http://localhost:{port}"
        self.active_tasks = {}
        
        # Initialize Flask app for A2A communication
        self.app = Flask(__name__)
        self.setup_routes()
        
        # Chart generation settings
        self.chart_config = {"responsive": True, "displayModeBar": True}
    
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
            "name": "ChartGenerationAgent",
            "description": "Creates portfolio analysis charts, graphs, and visual reports",
            "capabilities": [
                "generate_portfolio_pie_chart",
                "generate_holdings_bar_chart", 
                "generate_sector_allocation_chart",
                "generate_performance_chart",
                "generate_top_holdings_chart",
                "generate_interactive_dashboard"
            ],
            "endpoint": self.endpoint,
            "version": "1.0"
        }
    
    def execute_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a chart generation task"""
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
            if task_type == "generate_portfolio_pie_chart":
                result = self.generate_portfolio_pie_chart(data)
            elif task_type == "generate_holdings_bar_chart":
                result = self.generate_holdings_bar_chart(data)
            elif task_type == "generate_sector_allocation_chart":
                result = self.generate_sector_allocation_chart(data)
            elif task_type == "generate_performance_chart":
                result = self.generate_performance_chart(data)
            elif task_type == "generate_top_holdings_chart":
                result = self.generate_top_holdings_chart(data)
            elif task_type == "generate_interactive_dashboard":
                result = self.generate_interactive_dashboard(data)
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
    
    def generate_portfolio_pie_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a pie chart of portfolio allocation using Plotly"""
        holdings = data.get("holdings", [])
        title = data.get("title", "Portfolio Allocation")
        
        if not holdings:
            return {"error": "No holdings data provided"}
        
        top_10 = holdings[:10]
        symbols = [h["symbol"] for h in top_10]
        values = [h["market_value"] for h in top_10]
        
        # Create plotly pie chart
        fig = go.Figure(data=[go.Pie(
            labels=symbols,
            values=values,
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=f"{title}<br>Total Value: ${sum(values):,.2f}",
            font=dict(size=12),
            height=600,
            template="plotly_white"
        )
        
        chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return {
            "chart_type": "pie_chart",
            "title": title,
            "chart_json": chart_json,
            "chart_format": "plotly",
            "holdings_count": len(holdings),
            "top_holdings": top_10
        }
    
    def generate_holdings_bar_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a bar chart of top holdings using Plotly"""
        holdings = data.get("holdings", [])
        title = data.get("title", "Top 10 Holdings by Market Value")
        
        if not holdings:
            return {"error": "No holdings data provided"}
        
        top_10 = holdings[:10]
        symbols = [h["symbol"] for h in top_10]
        values = [h["market_value"] for h in top_10]
        percentages = [h["portfolio_percentage"] for h in top_10]
        
        # Create plotly bar chart
        fig = go.Figure(data=[go.Bar(
            x=symbols,
            y=values,
            text=[f"${v:,.0f}<br>({p:.1f}%)" for v, p in zip(values, percentages)],
            textposition='auto',
            marker_color='lightblue',
            hovertemplate='<b>%{x}</b><br>Market Value: $%{y:,.0f}<br>Portfolio %: %{customdata:.1f}%<extra></extra>',
            customdata=percentages
        )])
        
        fig.update_layout(
            title=title,
            xaxis_title="Symbol",
            yaxis_title="Market Value ($)",
            font=dict(size=12),
            height=600,
            template="plotly_white"
        )
        
        chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return {
            "chart_type": "bar_chart",
            "title": title,
            "chart_json": chart_json,
            "chart_format": "plotly",
            "top_holdings": top_10
        }
    
    def generate_sector_allocation_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sector allocation chart using Plotly"""
        holdings = data.get("holdings", [])
        title = data.get("title", "Portfolio Allocation by Sector")
        
        if not holdings:
            return {"error": "No holdings data provided"}
        
        # Aggregate by sector
        sector_allocation = {}
        for holding in holdings:
            sector = holding.get("sector", "Unknown")
            value = holding.get("market_value", 0)
            
            if sector not in sector_allocation:
                sector_allocation[sector] = {"value": 0, "count": 0}
            
            sector_allocation[sector]["value"] += value
            sector_allocation[sector]["count"] += 1
        
        sectors = list(sector_allocation.keys())
        values = [sector_allocation[s]["value"] for s in sectors]
        
        # Create plotly pie chart
        fig = go.Figure(data=[go.Pie(
            labels=sectors,
            values=values,
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<br>Holdings: %{customdata}<extra></extra>',
            customdata=[sector_allocation[s]["count"] for s in sectors]
        )])
        
        fig.update_layout(
            title=title,
            font=dict(size=12),
            height=600,
            template="plotly_white"
        )
        
        chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return {
            "chart_type": "sector_allocation",
            "title": title,
            "chart_json": chart_json,
            "chart_format": "plotly",
            "sector_breakdown": sector_allocation
        }
    
    def generate_performance_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance comparison chart using Plotly"""
        holdings = data.get("holdings", [])
        title = data.get("title", "Holdings Performance (Gain/Loss)")
        
        if not holdings:
            return {"error": "No holdings data provided"}
        
        top_10 = holdings[:10]
        symbols = [h["symbol"] for h in top_10]
        gains_losses = [h.get("unrealized_gain_loss", 0) for h in top_10]
        
        # Color bars based on gain/loss
        colors = ['green' if gl >= 0 else 'red' for gl in gains_losses]
        
        # Create plotly bar chart
        fig = go.Figure(data=[go.Bar(
            x=symbols,
            y=gains_losses,
            marker_color=colors,
            text=[f"${gl:,.0f}" for gl in gains_losses],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Gain/Loss: $%{y:,.0f}<extra></extra>'
        )])
        
        # Add horizontal line at zero
        fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
        
        fig.update_layout(
            title=title,
            xaxis_title="Symbol",
            yaxis_title="Unrealized Gain/Loss ($)",
            font=dict(size=12),
            height=600,
            template="plotly_white"
        )
        
        chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return {
            "chart_type": "performance_chart",
            "title": title,
            "chart_json": chart_json,
            "chart_format": "plotly",
            "performance_data": top_10
        }
    
    def generate_top_holdings_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive top holdings dashboard"""
        holdings = data.get("holdings", [])
        title = data.get("title", "Top 10 Stock Holdings Analysis")
        
        if not holdings:
            return {"error": "No holdings data provided"}
        
        # Create interactive plotly chart
        top_10 = holdings[:10]
        
        fig = go.Figure()
        
        # Add bar chart
        fig.add_trace(go.Bar(
            x=[h["symbol"] for h in top_10],
            y=[h["market_value"] for h in top_10],
            text=[f"${h['market_value']:,.0f}<br>({h['portfolio_percentage']:.1f}%)" for h in top_10],
            textposition='auto',
            name='Market Value',
            marker_color='lightblue',
            hovertemplate='<b>%{x}</b><br>' +
                         'Market Value: $%{y:,.0f}<br>' +
                         'Shares: %{customdata[0]:,.0f}<br>' +
                         'Price: $%{customdata[1]:.2f}<br>' +
                         'Sector: %{customdata[2]}<br>' +
                         '<extra></extra>',
            customdata=[[h.get("total_shares", 0), h.get("current_price", 0), h.get("sector", "Unknown")] for h in top_10]
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Symbol",
            yaxis_title="Market Value ($)",
            font=dict(size=12),
            height=600,
            showlegend=False,
            template="plotly_white"
        )
        
        # Convert to JSON for web display
        chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return {
            "chart_type": "interactive_top_holdings",
            "title": title,
            "chart_json": chart_json,
            "chart_format": "plotly",
            "top_holdings": top_10,
            "summary": {
                "total_value": sum(h["market_value"] for h in top_10),
                "average_allocation": sum(h["portfolio_percentage"] for h in top_10) / len(top_10),
                "largest_holding": top_10[0] if top_10 else None,
                "holdings_count": len(top_10)
            }
        }
    
    def generate_interactive_dashboard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete interactive dashboard"""
        holdings = data.get("holdings", [])
        client_data = data.get("client_data", {})
        
        if not holdings:
            return {"error": "No holdings data provided"}
        
        # Create subplot dashboard
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Top 10 Holdings', 'Sector Allocation', 'Performance', 'Portfolio Summary'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "table"}]]
        )
        
        top_10 = holdings[:10]
        
        # Top holdings bar chart
        fig.add_trace(go.Bar(
            x=[h["symbol"] for h in top_10],
            y=[h["market_value"] for h in top_10],
            name="Market Value",
            marker_color='lightblue'
        ), row=1, col=1)
        
        # Sector pie chart
        sector_data = {}
        for h in holdings:
            sector = h.get("sector", "Unknown")
            sector_data[sector] = sector_data.get(sector, 0) + h["market_value"]
        
        fig.add_trace(go.Pie(
            labels=list(sector_data.keys()),
            values=list(sector_data.values()),
            name="Sectors"
        ), row=1, col=2)
        
        # Performance chart
        fig.add_trace(go.Bar(
            x=[h["symbol"] for h in top_10],
            y=[h.get("unrealized_gain_loss", 0) for h in top_10],
            name="Gain/Loss",
            marker_color=['green' if h.get("unrealized_gain_loss", 0) >= 0 else 'red' for h in top_10]
        ), row=2, col=1)
        
        # Summary table
        table_data = [
            ["Total Portfolio Value", f"${sum(h['market_value'] for h in holdings):,.2f}"],
            ["Number of Holdings", str(len(holdings))],
            ["Largest Holding", f"{top_10[0]['symbol']} (${top_10[0]['market_value']:,.0f})" if top_10 else "N/A"],
            ["Top 10 Allocation", f"{sum(h['portfolio_percentage'] for h in top_10):.1f}%"],
            ["Total Gain/Loss", f"${sum(h.get('unrealized_gain_loss', 0) for h in holdings):,.2f}"]
        ]
        
        fig.add_trace(go.Table(
            header=dict(values=["Metric", "Value"]),
            cells=dict(values=[[row[0] for row in table_data], [row[1] for row in table_data]])
        ), row=2, col=2)
        
        fig.update_layout(
            title="Portfolio Dashboard",
            height=800,
            showlegend=False,
            template="plotly_white"
        )
        
        chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return {
            "chart_type": "interactive_dashboard",
            "title": "Portfolio Dashboard",
            "chart_json": chart_json,
            "chart_format": "plotly",
            "summary": {
                "total_value": sum(h["market_value"] for h in holdings),
                "holdings_count": len(holdings),
                "top_10_value": sum(h["market_value"] for h in top_10),
                "total_gain_loss": sum(h.get("unrealized_gain_loss", 0) for h in holdings)
            }
        }
    
    def start_server(self):
        """Start the A2A protocol server"""
        print(f"Starting ChartGeneration agent on port {self.port}")
        print(f"Agent Card: {json.dumps(self.get_agent_card(), indent=2)}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

if __name__ == "__main__":
    agent = ChartGenerationAgent()
    agent.start_server()