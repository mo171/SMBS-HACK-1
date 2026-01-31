from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any


class NodeParams(BaseModel):
    """Flexible parameters for workflow nodes. Can contain any key-value pairs."""

    model_config = ConfigDict(extra="allow")


class NodeData(BaseModel):
    service: str
    task: str
    # Use a concrete dict or a string-based params field
    params: dict = Field(default_factory=dict)


class WorkflowNode(BaseModel):
    id: str
    type: str
    data: NodeData
    # React Flow MUST have position
    position: dict = Field(default={"x": 250, "y": 250})


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str


class WorkflowBlueprint(BaseModel):
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
