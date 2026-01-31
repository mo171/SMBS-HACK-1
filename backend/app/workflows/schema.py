from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class NodeData(BaseModel):
    service: str = Field(description="The service name, e.g., 'razorpay', 'whatsapp', 'google_sheets'")
    task: str = Field(description="The specific action or event, e.g., 'payment_captured', 'send_message'")
    params: Optional[Dict[str, Any]] = Field(description="Parameters like message text or sheet name")

class WorkflowNode(BaseModel):
    id: str
    type: str = Field(description="Either 'trigger' or 'action'")
    data: NodeData

class WorkflowEdge(BaseModel):
    id: str
    source: str = Field(description="The ID of the starting node")
    target: str = Field(description="The ID of the destination node")

class WorkflowBlueprint(BaseModel):
    name: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]