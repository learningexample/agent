"""
Google Agent2Agent Protocol Implementation
Core A2A protocol utilities and message handling
"""

import json
import requests
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class A2AMessageType(Enum):
    """A2A Protocol Message Types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"

@dataclass
class A2AMessage:
    """A2A Protocol Message Structure based on JSON-RPC 2.0"""
    jsonrpc: str = "2.0"
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create A2AMessage from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class AgentCapability:
    """Individual agent capability definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    
@dataclass 
class AgentCard:
    """Agent capability advertisement following A2A specification"""
    name: str
    description: str
    version: str
    endpoint: str
    capabilities: List[AgentCapability]
    supported_modalities: List[str] = None
    authentication_schemes: List[str] = None
    
    def __post_init__(self):
        if self.supported_modalities is None:
            self.supported_modalities = ["text", "json"]
        if self.authentication_schemes is None:
            self.authentication_schemes = ["none", "bearer"]

class A2AProtocolClient:
    """Client for communicating with A2A protocol agents"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "A2A-Client/1.0"
        })
    
    def discover_capabilities(self, agent_endpoint: str) -> Optional[AgentCard]:
        """Discover agent capabilities via A2A protocol"""
        message = A2AMessage(
            method="get_capabilities",
            params={},
            id=f"discover_{int(time.time())}"
        )
        
        try:
            response = self.session.post(
                f"{agent_endpoint}/a2a",
                json=message.to_dict(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    card_data = result["result"]
                    # Convert simple capability list to AgentCapability objects
                    capabilities = []
                    for cap_name in card_data.get("capabilities", []):
                        capabilities.append(AgentCapability(
                            name=cap_name,
                            description=f"Capability: {cap_name}",
                            input_schema={},
                            output_schema={}
                        ))
                    
                    return AgentCard(
                        name=card_data["name"],
                        description=card_data["description"],
                        version=card_data["version"],
                        endpoint=card_data["endpoint"],
                        capabilities=capabilities
                    )
            
        except Exception as e:
            print(f"Capability discovery failed for {agent_endpoint}: {e}")
        
        return None
    
    def send_task(self, agent_endpoint: str, task_method: str, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a task to an agent using A2A protocol"""
        message = A2AMessage(
            method=task_method,
            params=task_params,
            id=f"task_{int(time.time())}"
        )
        
        try:
            response = self.session.post(
                f"{agent_endpoint}/a2a",
                json=message.to_dict(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": {
                        "code": response.status_code,
                        "message": f"HTTP Error: {response.status_code}"
                    }
                }
                
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Communication error: {str(e)}"
                }
            }
    
    def send_notification(self, agent_endpoint: str, method: str, params: Dict[str, Any]) -> bool:
        """Send a notification (no response expected) to an agent"""
        message = A2AMessage(
            method=method,
            params=params
            # Note: notifications don't have an id field
        )
        
        try:
            response = self.session.post(
                f"{agent_endpoint}/a2a",
                json=message.to_dict(),
                timeout=self.timeout
            )
            return response.status_code == 200
            
        except Exception as e:
            print(f"Notification failed: {e}")
            return False

class A2AProtocolServer:
    """Base server implementation for A2A protocol agents"""
    
    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card
        self.request_handlers = {}
        self.notification_handlers = {}
        
        # Register default handlers
        self.register_request_handler("get_capabilities", self._handle_get_capabilities)
    
    def register_request_handler(self, method: str, handler):
        """Register a handler for request messages"""
        self.request_handlers[method] = handler
    
    def register_notification_handler(self, method: str, handler):
        """Register a handler for notification messages"""
        self.notification_handlers[method] = handler
    
    def _handle_get_capabilities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capability discovery requests"""
        return asdict(self.agent_card)
    
    def process_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming A2A protocol message"""
        try:
            message = A2AMessage.from_dict(message_data)
            
            # Validate JSON-RPC version
            if message.jsonrpc != "2.0":
                return self._create_error_response(
                    -32600, "Invalid Request", message.id
                )
            
            # Handle request messages (expect response)
            if message.id is not None and message.method:
                if message.method in self.request_handlers:
                    try:
                        result = self.request_handlers[message.method](
                            message.params or {}
                        )
                        return A2AMessage(
                            jsonrpc="2.0",
                            result=result,
                            id=message.id
                        ).to_dict()
                    except Exception as e:
                        return self._create_error_response(
                            -32603, f"Internal error: {str(e)}", message.id
                        )
                else:
                    return self._create_error_response(
                        -32601, "Method not found", message.id
                    )
            
            # Handle notification messages (no response)
            elif message.id is None and message.method:
                if message.method in self.notification_handlers:
                    try:
                        self.notification_handlers[message.method](
                            message.params or {}
                        )
                    except Exception as e:
                        print(f"Notification handler error: {e}")
                return None
            
            else:
                return self._create_error_response(
                    -32600, "Invalid Request", message.id
                )
                
        except Exception as e:
            return self._create_error_response(
                -32700, f"Parse error: {str(e)}", None
            )
    
    def _create_error_response(self, code: int, message: str, request_id: Optional[str]) -> Dict[str, Any]:
        """Create standardized error response"""
        return A2AMessage(
            jsonrpc="2.0",
            error={"code": code, "message": message},
            id=request_id
        ).to_dict()

class A2ATaskManager:
    """Manages long-running tasks in A2A protocol"""
    
    def __init__(self):
        self.tasks = {}
    
    def create_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        task = {
            "id": task_id,
            "status": "created",
            "created_at": time.time(),
            "data": task_data,
            "progress": 0,
            "result": None,
            "error": None
        }
        self.tasks[task_id] = task
        return task
    
    def update_task_status(self, task_id: str, status: str, progress: int = None, result: Any = None, error: str = None):
        """Update task status"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = time.time()
            
            if progress is not None:
                self.tasks[task_id]["progress"] = progress
            if result is not None:
                self.tasks[task_id]["result"] = result
            if error is not None:
                self.tasks[task_id]["error"] = error
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks"""
        return list(self.tasks.values())

# A2A Protocol Error Codes (following JSON-RPC 2.0)
A2A_ERROR_CODES = {
    -32700: "Parse error",
    -32600: "Invalid Request", 
    -32601: "Method not found",
    -32602: "Invalid params",
    -32603: "Internal error",
    -32000: "Server error",  # A2A specific errors start here
    -32001: "Agent unavailable",
    -32002: "Capability not supported",
    -32003: "Authentication required",
    -32004: "Permission denied",
    -32005: "Rate limit exceeded"
}