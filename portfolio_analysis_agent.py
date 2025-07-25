"""
Portfolio Analysis Agent with LLM Integration
Enhanced A2A agent that provides AI-powered portfolio analysis and insights
"""

import json
import time
import pandas as pd
import os
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from dataclasses import dataclass, asdict

from llm_service import get_llm_service, LLMRequest, generate_text
from a2a_protocol import A2AProtocolServer, AgentCard, AgentCapability

@dataclass
class A2AMessage:
    """A2A Protocol Message Structure"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = None
    id: str = ""

class PortfolioAnalysisAgent:
    """LLM-enhanced agent for portfolio analysis and insights"""
    
    def __init__(self, name: str = "PortfolioAnalysisAgent", port: int = 8006):
        self.name = name
        self.port = port
        self.endpoint = f"http://localhost:{port}"
        self.llm_service = get_llm_service()
        self.active_tasks = {}
        
        # Initialize Flask app for A2A communication
        self.app = Flask(__name__)
        self.setup_routes()
        
        # Load reference data for context
        self.market_data = self.load_market_data()
        self.client_data = self.load_client_data()
        
        # Create agent capabilities
        self.agent_card = AgentCard(
            name=self.name,
            description="AI-powered portfolio analysis agent providing intelligent insights and recommendations",
            version="1.0",
            endpoint=self.endpoint,
            capabilities=[
                AgentCapability(
                    name="portfolio_analysis_llm",
                    description="Generate comprehensive portfolio analysis using AI insights",
                    input_schema={"client_id": "string", "analysis_type": "string"},
                    output_schema={"analysis": "string", "insights": "array", "recommendations": "array"}
                ),
                AgentCapability(
                    name="market_commentary",
                    description="Generate market commentary and outlook using AI analysis",
                    input_schema={"holdings": "array", "market_conditions": "object"},
                    output_schema={"commentary": "string", "outlook": "string"}
                ),
                AgentCapability(
                    name="risk_assessment_llm",
                    description="AI-powered risk assessment and analysis",
                    input_schema={"portfolio_data": "object"},
                    output_schema={"risk_analysis": "string", "risk_score": "number", "recommendations": "array"}
                ),
                AgentCapability(
                    name="investment_insights",
                    description="Generate investment insights and strategic recommendations",
                    input_schema={"portfolio_summary": "object", "objectives": "string"},
                    output_schema={"insights": "string", "strategy": "array", "next_steps": "array"}
                )
            ]
        )
        
        # Setup A2A protocol server
        self.a2a_server = A2AProtocolServer(self.agent_card)
        self.register_handlers()
    
    def load_market_data(self) -> Dict[str, Any]:
        """Load market data for context"""
        try:
            if os.path.exists('data/market_data.csv'):
                df = pd.read_csv('data/market_data.csv')
                return df.set_index('symbol').to_dict('index')
        except Exception as e:
            print(f"Warning: Could not load market data: {e}")
        return {}
    
    def load_client_data(self) -> Dict[str, Any]:
        """Load client data for context"""
        try:
            if os.path.exists('data/clients.csv'):
                df = pd.read_csv('data/clients.csv')
                return df.set_index('client_id').to_dict('index')
        except Exception as e:
            print(f"Warning: Could not load client data: {e}")
        return {}
    
    def setup_routes(self):
        """Setup Flask routes for A2A communication"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                "status": "healthy",
                "agent": self.name,
                "llm_available": self.llm_service.get_available_service().is_available(),
                "llm_status": self.llm_service.get_service_status()
            })
        
        @self.app.route('/a2a', methods=['POST'])
        def handle_a2a_message():
            try:
                message_data = request.get_json()
                response = self.a2a_server.process_message(message_data)
                
                if response:
                    return jsonify(response)
                else:
                    return '', 204  # No content for notifications
                    
            except Exception as e:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    },
                    "id": message_data.get("id")
                }), 500
    
    def register_handlers(self):
        """Register A2A message handlers"""
        self.a2a_server.register_request_handler("execute_task", self.handle_execute_task)
        
    def handle_execute_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task execution requests"""
        task_id = params.get("task_id", f"task_{int(time.time())}")
        task_type = params.get("task_type", "")
        data = params.get("data", {})
        context = params.get("context", {})
        
        self.active_tasks[task_id] = {
            "status": "processing",
            "start_time": time.time(),
            "task_type": task_type
        }
        
        try:
            if task_type == "portfolio_analysis_llm":
                result = self.generate_portfolio_analysis(data, context)
            elif task_type == "market_commentary":
                result = self.generate_market_commentary(data, context)
            elif task_type == "risk_assessment_llm":
                result = self.generate_risk_assessment(data, context)
            elif task_type == "investment_insights":
                result = self.generate_investment_insights(data, context)
            else:
                result = {"error": f"Unknown task type: {task_type}"}
            
            # Update task status
            self.active_tasks[task_id].update({
                "status": "completed",
                "end_time": time.time(),
                "result": result
            })
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "processing_time": time.time() - self.active_tasks[task_id]["start_time"],
                "llm_provider": self.llm_service.get_available_service().get_model_info()["provider"]
            }
            
        except Exception as e:
            self.active_tasks[task_id].update({
                "status": "failed",
                "end_time": time.time(),
                "error": str(e)
            })
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "processing_time": time.time() - self.active_tasks[task_id]["start_time"]
            }
    
    def generate_portfolio_analysis(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive portfolio analysis using LLM"""
        client_id = data.get("client_id")
        holdings = data.get("holdings", [])
        
        # Prepare portfolio summary for LLM context
        total_value = sum(float(h.get("market_value", 0)) for h in holdings)
        num_holdings = len(holdings)
        top_holdings = sorted(holdings, key=lambda x: float(x.get("market_value", 0)), reverse=True)[:10]
        
        # Create sector distribution
        sectors = {}
        for holding in holdings:
            symbol = holding.get("symbol", "")
            market_info = self.market_data.get(symbol, {})
            sector = market_info.get("sector", "Unknown")
            sectors[sector] = sectors.get(sector, 0) + float(holding.get("market_value", 0))
        
        # Get client information
        client_info = self.client_data.get(client_id, {})
        client_name = client_info.get("client_name", client_id)
        
        # Construct LLM prompt
        prompt = f"""
        Please analyze the following portfolio for {client_name} (ID: {client_id}):
        
        Portfolio Summary:
        - Total Portfolio Value: ${total_value:,.2f}
        - Number of Holdings: {num_holdings}
        - Client Type: {self._classify_client_type(client_name)}
        
        Top 10 Holdings:
        {self._format_holdings_for_prompt(top_holdings[:10])}
        
        Sector Distribution:
        {self._format_sectors_for_prompt(sectors)}
        
        Please provide:
        1. Overall portfolio assessment
        2. Strengths and potential concerns
        3. Diversification analysis
        4. Strategic recommendations
        5. Risk considerations
        
        Focus on institutional-level analysis appropriate for this client type.
        """
        
        system_prompt = "You are a senior portfolio analyst with expertise in institutional investment management. Provide professional, data-driven analysis with specific insights and actionable recommendations."
        
        # Generate analysis using LLM
        llm_response = generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            temperature=0.3,
            context={
                "total_value": total_value,
                "num_holdings": num_holdings,
                "client_type": self._classify_client_type(client_name)
            }
        )
        
        return {
            "client_id": client_id,
            "client_name": client_name,
            "portfolio_summary": {
                "total_value": total_value,
                "num_holdings": num_holdings,
                "top_holdings": top_holdings[:5],
                "sector_distribution": sectors
            },
            "llm_analysis": llm_response.content,
            "analysis_metadata": {
                "provider": llm_response.provider,
                "model": llm_response.model,
                "tokens_used": llm_response.tokens_used,
                "processing_time": llm_response.processing_time,
                "success": llm_response.success
            }
        }
    
    def generate_market_commentary(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market commentary using LLM"""
        holdings = data.get("holdings", [])
        market_conditions = data.get("market_conditions", {})
        
        # Analyze portfolio exposure
        sectors_exposure = self._calculate_sector_exposure(holdings)
        major_positions = [h for h in holdings if float(h.get("market_value", 0)) > 10000000]  # >$10M positions
        
        prompt = f"""
        Provide market commentary and outlook based on the following portfolio exposure:
        
        Major Sector Exposures:
        {self._format_sectors_for_prompt(sectors_exposure)}
        
        Significant Positions (>$10M):
        {self._format_holdings_for_prompt(major_positions)}
        
        Please provide:
        1. Current market environment assessment
        2. Sector-specific outlook based on portfolio exposure
        3. Key risks and opportunities
        4. Short-term and medium-term market outlook
        5. Positioning recommendations
        """
        
        system_prompt = "You are a senior market strategist providing institutional-level market commentary. Focus on actionable insights and strategic positioning advice."
        
        llm_response = generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1200,
            temperature=0.4
        )
        
        return {
            "market_commentary": llm_response.content,
            "sector_exposure": sectors_exposure,
            "major_positions_count": len(major_positions),
            "commentary_metadata": {
                "provider": llm_response.provider,
                "model": llm_response.model,
                "tokens_used": llm_response.tokens_used,
                "processing_time": llm_response.processing_time
            }
        }
    
    def generate_risk_assessment(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk assessment using LLM"""
        portfolio_data = data.get("portfolio_data", {})
        holdings = portfolio_data.get("holdings", [])
        
        # Calculate basic risk metrics
        total_value = sum(float(h.get("market_value", 0)) for h in holdings)
        concentration_risk = self._calculate_concentration_risk(holdings, total_value)
        sector_concentration = self._calculate_sector_concentration(holdings)
        
        prompt = f"""
        Assess the risk profile of this portfolio:
        
        Portfolio Characteristics:
        - Total Value: ${total_value:,.2f}
        - Number of Holdings: {len(holdings)}
        - Top 10 Concentration: {concentration_risk['top_10_percentage']:.1f}%
        - Largest Single Position: {concentration_risk['largest_position_percentage']:.1f}%
        
        Sector Concentration Analysis:
        {self._format_concentration_analysis(sector_concentration)}
        
        Please provide:
        1. Overall risk assessment and risk score (1-10, where 10 is highest risk)
        2. Key risk factors and concerns
        3. Concentration risk analysis
        4. Diversification effectiveness
        5. Risk mitigation recommendations
        """
        
        system_prompt = "You are a senior risk analyst specializing in institutional portfolio risk assessment. Provide quantitative insights and specific risk management recommendations."
        
        llm_response = generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1300,
            temperature=0.2
        )
        
        return {
            "risk_analysis": llm_response.content,
            "risk_metrics": {
                "concentration_risk": concentration_risk,
                "sector_concentration": sector_concentration,
                "portfolio_size": len(holdings),
                "total_value": total_value
            },
            "risk_metadata": {
                "provider": llm_response.provider,
                "model": llm_response.model,
                "tokens_used": llm_response.tokens_used,
                "processing_time": llm_response.processing_time
            }
        }
    
    def generate_investment_insights(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment insights and strategic recommendations"""
        portfolio_summary = data.get("portfolio_summary", {})
        objectives = data.get("objectives", "growth and income")
        
        prompt = f"""
        Provide strategic investment insights for this institutional portfolio:
        
        Portfolio Overview:
        - Total Assets: ${portfolio_summary.get('total_value', 0):,.2f}
        - Holdings Count: {portfolio_summary.get('num_holdings', 0)}
        - Investment Objectives: {objectives}
        
        Current Allocation Summary:
        {self._format_portfolio_summary(portfolio_summary)}
        
        Please provide:
        1. Strategic investment insights and themes
        2. Portfolio positioning analysis
        3. Tactical allocation recommendations
        4. Emerging opportunities and trends
        5. Next steps and action items
        """
        
        system_prompt = "You are a senior investment strategist providing institutional-level strategic guidance. Focus on strategic themes, positioning insights, and actionable recommendations."
        
        llm_response = generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1400,
            temperature=0.5
        )
        
        return {
            "investment_insights": llm_response.content,
            "portfolio_overview": portfolio_summary,
            "objectives": objectives,
            "insights_metadata": {
                "provider": llm_response.provider,
                "model": llm_response.model,
                "tokens_used": llm_response.tokens_used,
                "processing_time": llm_response.processing_time
            }
        }
    
    def _classify_client_type(self, client_name: str) -> str:
        """Classify client type based on name"""
        name_lower = client_name.lower()
        if any(word in name_lower for word in ['pension', 'retirement', 'calpers']):
            return "Pension Fund"
        elif any(word in name_lower for word in ['capital', 'partners', 'management', 'fund']):
            return "Hedge Fund / Private Equity"
        elif any(word in name_lower for word in ['asset management', 'investments', 'advisors']):
            return "Asset Management"
        else:
            return "Institutional Investor"
    
    def _format_holdings_for_prompt(self, holdings: List[Dict]) -> str:
        """Format holdings data for LLM prompt"""
        lines = []
        for i, holding in enumerate(holdings, 1):
            symbol = holding.get("symbol", "")
            market_value = float(holding.get("market_value", 0))
            lines.append(f"{i}. {symbol}: ${market_value:,.0f}")
        return "\n".join(lines)
    
    def _format_sectors_for_prompt(self, sectors: Dict[str, float]) -> str:
        """Format sector distribution for LLM prompt"""
        sorted_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)
        lines = []
        total = sum(sectors.values())
        for sector, value in sorted_sectors:
            percentage = (value / total) * 100 if total > 0 else 0
            lines.append(f"- {sector}: ${value:,.0f} ({percentage:.1f}%)")
        return "\n".join(lines)
    
    def _calculate_sector_exposure(self, holdings: List[Dict]) -> Dict[str, float]:
        """Calculate sector exposure from holdings"""
        sectors = {}
        for holding in holdings:
            symbol = holding.get("symbol", "")
            market_info = self.market_data.get(symbol, {})
            sector = market_info.get("sector", "Unknown")
            value = float(holding.get("market_value", 0))
            sectors[sector] = sectors.get(sector, 0) + value
        return sectors
    
    def _calculate_concentration_risk(self, holdings: List[Dict], total_value: float) -> Dict[str, Any]:
        """Calculate concentration risk metrics"""
        sorted_holdings = sorted(holdings, key=lambda x: float(x.get("market_value", 0)), reverse=True)
        
        top_10_value = sum(float(h.get("market_value", 0)) for h in sorted_holdings[:10])
        largest_position_value = float(sorted_holdings[0].get("market_value", 0)) if sorted_holdings else 0
        
        return {
            "top_10_percentage": (top_10_value / total_value) * 100 if total_value > 0 else 0,
            "largest_position_percentage": (largest_position_value / total_value) * 100 if total_value > 0 else 0,
            "top_10_value": top_10_value,
            "largest_position_value": largest_position_value
        }
    
    def _calculate_sector_concentration(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Calculate sector concentration"""
        sectors = self._calculate_sector_exposure(holdings)
        total_value = sum(sectors.values())
        
        # Calculate Herfindahl-Hirschman Index for sector concentration
        hhi = sum((value / total_value) ** 2 for value in sectors.values()) if total_value > 0 else 0
        
        return {
            "herfindahl_index": hhi,
            "num_sectors": len(sectors),
            "largest_sector_percentage": max(sectors.values()) / total_value * 100 if total_value > 0 else 0,
            "sector_distribution": sectors
        }
    
    def _format_concentration_analysis(self, concentration: Dict[str, Any]) -> str:
        """Format concentration analysis for prompt"""
        return f"""
        - Herfindahl Index: {concentration['herfindahl_index']:.3f}
        - Number of Sectors: {concentration['num_sectors']}
        - Largest Sector: {concentration['largest_sector_percentage']:.1f}%
        """
    
    def _format_portfolio_summary(self, summary: Dict[str, Any]) -> str:
        """Format portfolio summary for prompt"""
        lines = [
            f"Total Value: ${summary.get('total_value', 0):,.2f}",
            f"Holdings: {summary.get('num_holdings', 0)} positions"
        ]
        
        if "sector_distribution" in summary:
            lines.append("Top Sectors:")
            sectors = summary["sector_distribution"]
            total = sum(sectors.values()) if sectors else 1
            for sector, value in sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:5]:
                pct = (value / total) * 100
                lines.append(f"  - {sector}: {pct:.1f}%")
        
        return "\n".join(lines)
    
    def run(self):
        """Start the agent server"""
        print(f"Starting {self.name} on port {self.port}")
        print(f"LLM Service Status: {self.llm_service.get_service_status()}")
        print(f"Agent endpoint: {self.endpoint}")
        print(f"Available capabilities: {[cap.name for cap in self.agent_card.capabilities]}")
        
        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
        except KeyboardInterrupt:
            print(f"\n{self.name} shutting down...")

if __name__ == "__main__":
    agent = PortfolioAnalysisAgent()
    agent.run()