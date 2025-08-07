from typing import Annotated, Any, Dict, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langgraph.prebuilt.chat_agent_executor import AgentState


class WokwiAgentState(AgentState):
    """Extended agent state with circuit-specific context."""
    circuit_context: Dict[str, Any]
    user_intent: str
    component_count: int


class CircuitContext(TypedDict):
    components: Dict[str, Dict[str, Any]]
    connections: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class ComponentData(TypedDict):
    type: str
    id: str
    position: Dict[str, float]
    properties: Dict[str, Any]


class ConnectionData(TypedDict):
    from_component: str
    from_pin: str
    to_component: str
    to_pin: str
    wire_color: str