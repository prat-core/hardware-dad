"""
Circuit state management for Wokwi component tools.
"""

from typing import List, Dict, Any, Optional
import sys
import os

# Add the parent directory to Python path to import wokwi_components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wokwi_components.base import Component


class CircuitManager:
    """Singleton class to manage circuit state across tool calls"""
    _instance = None
    
    def __init__(self):
        if CircuitManager._instance is not None:
            raise Exception("CircuitManager is a singleton class. Use get_instance() method.")
        self.components: List[Component] = []
        self.connections: List[Dict[str, Any]] = []
        self.component_counter: Dict[str, int] = {}
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of CircuitManager"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def add_component(self, component: Component) -> str:
        """Add a component to the circuit"""
        self.components.append(component)
        return f"Added {component.type.value} with ID: {component.id}"
    
    def add_connection(self, from_component: str, from_pin: str, 
                      to_component: str, to_pin: str, color: str = "green", wire_routing: list = None) -> str:
        """Add a connection between two components"""
        if wire_routing is None:
            wire_routing = []
        connection = {
            "from": f"{from_component}:{from_pin}",
            "to": f"{to_component}:{to_pin}",
            "color": color,
            "wire_routing": wire_routing
        }
        self.connections.append(connection)
        return f"Connected {from_component}:{from_pin} to {to_component}:{to_pin}"
    
    def list_components(self) -> List[Dict[str, Any]]:
        """List all components in the circuit"""
        return [
            {
                "id": comp.id,
                "type": comp.type.value,
                "position": {"top": comp.top, "left": comp.left},
                "attrs": comp.attrs
            }
            for comp in self.components
        ]
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """List all connections in the circuit"""
        return self.connections.copy()
    
    def clear_circuit(self) -> str:
        """Clear all components and connections"""
        self.components.clear()
        self.connections.clear()
        self.component_counter.clear()
        return "Circuit cleared successfully"
    
    def generate_component_id(self, component_type: str) -> str:
        """Generate unique component ID"""
        counter = self.component_counter.get(component_type, 0)
        self.component_counter[component_type] = counter + 1
        return f"{component_type}_{counter + 1}"
    
    def component_exists(self, component_id: str) -> bool:
        """Check if a component with given ID exists"""
        return any(comp.id == component_id for comp in self.components)
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """Get component by ID"""
        for comp in self.components:
            if comp.id == component_id:
                return comp
        return None