"""
LangChain tools for adding and managing Wokwi components.
"""

import json
import sys
import os
from typing import Optional

# Add the parent directory to Python path to import wokwi_components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from wokwi_components.arduino import ArduinoUno
from wokwi_components.led import LED
from wokwi_components.servo import Servo
from wokwi_components.serializer import to_wokwi_format
from .circuit_manager import CircuitManager


class AddArduinoInput(BaseModel):
    """Input schema for adding Arduino Uno"""
    top: float = Field(default=0, description="Top position in pixels")
    left: float = Field(default=0, description="Left position in pixels") 
    component_id: Optional[str] = Field(default=None, description="Optional custom component ID")


class AddLEDInput(BaseModel):
    """Input schema for adding LED"""
    top: float = Field(default=90, description="Top position in pixels")
    left: float = Field(default=9, description="Left position in pixels")
    color: Optional[str] = Field(default=None, description="LED color (red, green, blue, yellow, etc.)")
    component_id: Optional[str] = Field(default=None, description="Optional custom component ID")


class AddServoInput(BaseModel):
    """Input schema for adding Servo motor"""
    top: float = Field(default=0, description="Top position in pixels")
    left: float = Field(default=0, description="Left position in pixels")
    component_id: Optional[str] = Field(default=None, description="Optional custom component ID")


class AddConnectionInput(BaseModel):
    """Input schema for adding connection between components"""
    from_component: str = Field(description="Source component ID")
    from_pin: str = Field(description="Source component pin name")
    to_component: str = Field(description="Target component ID")  
    to_pin: str = Field(description="Target component pin name")
    color: str = Field(default="green", description="Connection wire color")
    wire_routing: list = Field(default_factory=list, description="Wire routing instructions")


@tool("add_arduino", args_schema=AddArduinoInput)
def add_arduino(top: float = 0, left: float = 0, component_id: Optional[str] = None) -> str:
    """Add an Arduino Uno to the circuit at specified position"""
    circuit_manager = CircuitManager.get_instance()
    
    if component_id is None:
        component_id = circuit_manager.generate_component_id("arduino")
    elif circuit_manager.component_exists(component_id):
        return f"Error: Component with ID '{component_id}' already exists"
    
    arduino = ArduinoUno(component_id=component_id, top=top, left=left)
    return circuit_manager.add_component(arduino)


@tool("add_led", args_schema=AddLEDInput)  
def add_led(top: float = 0, left: float = 0, color: Optional[str] = None, 
           component_id: Optional[str] = None) -> str:
    """Add an LED to the circuit at specified position with optional color"""
    circuit_manager = CircuitManager.get_instance()
    
    if component_id is None:
        component_id = circuit_manager.generate_component_id("led")
    elif circuit_manager.component_exists(component_id):
        return f"Error: Component with ID '{component_id}' already exists"
    
    led = LED(component_id=component_id, top=top, left=left, color=color)
    return circuit_manager.add_component(led)


@tool("add_servo", args_schema=AddServoInput)
def add_servo(top: float = 0, left: float = 0, component_id: Optional[str] = None) -> str:
    """Add a servo motor to the circuit at specified position"""
    circuit_manager = CircuitManager.get_instance()
    
    if component_id is None:
        component_id = circuit_manager.generate_component_id("servo")
    elif circuit_manager.component_exists(component_id):
        return f"Error: Component with ID '{component_id}' already exists"
        
    servo = Servo(component_id=component_id, top=top, left=left)
    return circuit_manager.add_component(servo)


@tool("add_connection", args_schema=AddConnectionInput)
def add_connection(from_component: str, from_pin: str, to_component: str, 
                  to_pin: str, color: str = "green", wire_routing: list = None) -> str:
    """Create an electrical connection between two component pins"""
    circuit_manager = CircuitManager.get_instance()
    
    # Validate components exist
    if not circuit_manager.component_exists(from_component):
        return f"Error: Component '{from_component}' not found"
    if not circuit_manager.component_exists(to_component):
        return f"Error: Component '{to_component}' not found"
    
    if wire_routing is None:
        wire_routing = []
    
    return circuit_manager.add_connection(from_component, from_pin, to_component, to_pin, color, wire_routing)


@tool("list_components")
def list_components() -> str:
    """List all components currently in the circuit"""
    circuit_manager = CircuitManager.get_instance()
    components = circuit_manager.list_components()
    connections = circuit_manager.list_connections()
    
    result = {
        "components": components,
        "connections": connections
    }
    
    return json.dumps(result, indent=2)


@tool("clear_circuit") 
def clear_circuit() -> str:
    """Clear all components and connections from the circuit"""
    circuit_manager = CircuitManager.get_instance()
    return circuit_manager.clear_circuit()


@tool("generate_diagram")
def generate_diagram() -> str:
    """Generate final Wokwi diagram.json for the current circuit"""
    circuit_manager = CircuitManager.get_instance()
    
    if not circuit_manager.components:
        return "Error: No components in circuit. Add some components first."
    
    # Convert connections to the format expected by serializer
    connections = []
    for conn in circuit_manager.connections:
        connections.append([
            conn["from"],
            conn["to"], 
            conn.get("color", "green"),
            conn.get("wire_routing", [])  # Use wire routing or empty array
        ])
    
    diagram = to_wokwi_format(circuit_manager.components, connections)
    
    # Format JSON to match the intended compact style
    def format_wokwi_json(data):
        """Format JSON in the compact Wokwi style"""
        result = "{\n"
        result += f'  "version": {data["version"]},\n'
        result += f'  "author": "{data["author"]}",\n' 
        result += f'  "editor": "{data["editor"]}",\n'
        
        # Format parts array with each part on one line
        result += '  "parts": [\n'
        for i, part in enumerate(data["parts"]):
            comma = "," if i < len(data["parts"]) - 1 else ""
            attrs_str = json.dumps(part["attrs"], separators=(',', ':'))
            result += f'    {{ "type": "{part["type"]}", "id": "{part["id"]}", "top": {part["top"]}, "left": {part["left"]}, "attrs": {attrs_str} }}{comma}\n'
        result += '  ],\n'
        
        # Format connections array
        result += '  "connections": [\n'
        for i, conn in enumerate(data["connections"]):
            comma = "," if i < len(data["connections"]) - 1 else ""
            result += f'    [ "{conn[0]}", "{conn[1]}", "{conn[2]}", {json.dumps(conn[3])} ]{comma}\n'
        result += '  ],\n'
        
        result += f'  "dependencies": {json.dumps(data["dependencies"])}\n'
        result += "}"
        
        # save result to a file 
        with open("diagram.json", "w") as f:
            f.write(result)
        return result
    
    
    
    return format_wokwi_json(diagram)