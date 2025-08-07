"""
Wokwi component tools for LangChain/LangGraph agent integration.
"""

from langchain_core.tools import tool
from typing import List, Optional
import json

# Import existing tools
import sys
import os

# Add the tools directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from component_tools import (
    add_arduino, add_led, add_servo, add_connection,
    list_components, clear_circuit, generate_diagram
)
from circuit_parser import CircuitParser, CircuitValidator, ComponentSpec, ConnectionSpec
from circuit_manager import CircuitManager


@tool
def parse_circuit_description(description: str) -> str:
    """Parse a natural language circuit description and extract components and connections."""
    parser = CircuitParser()
    validator = CircuitValidator()
    
    # Parse components and connections
    components = parser.parse_components(description)
    connections = parser.parse_connections(description, components)
    
    # Validate the circuit
    is_valid, errors = parser.validate_circuit(components, connections)
    if not is_valid:
        return json.dumps({
            "error": "Circuit validation failed",
            "errors": errors,
            "components": [{"type": c.type, "name": c.name, "properties": c.properties} for c in components],
            "connections": [{"from": c.from_component, "to": c.to_component} for c in connections]
        }, indent=2)
    
    # Additional electrical validation
    is_electrically_valid, electrical_errors = validator.validate_connections(connections)
    component_limits_valid, component_errors = validator.check_component_limits(components)
    
    all_errors = electrical_errors + component_errors
    if all_errors:
        return json.dumps({
            "warning": "Circuit has potential issues",
            "warnings": all_errors,
            "components": [{"type": c.type, "name": c.name, "properties": c.properties} for c in components],
            "connections": [{"from": c.from_component, "to": c.to_component} for c in connections]
        }, indent=2)
    
    return json.dumps({
        "success": "Circuit parsed successfully",
        "components": [{"type": c.type, "name": c.name, "properties": c.properties} for c in components],
        "connections": [{"from": c.from_component, "to": c.to_component} for c in connections]
    }, indent=2)


@tool
def build_circuit_from_description(description: str) -> str:
    """Build a complete circuit from natural language description."""
    parser = CircuitParser()
    validator = CircuitValidator()
    circuit_manager = CircuitManager.get_instance()
    
    # Clear existing circuit
    circuit_manager.clear_circuit()
    
    # Parse the description
    components = parser.parse_components(description)
    connections = parser.parse_connections(description, components)
    
    # Validate before building
    is_valid, errors = parser.validate_circuit(components, connections)
    if not is_valid:
        return f"Cannot build circuit due to validation errors: {', '.join(errors)}"
    
    results = []
    
    # Add components with automatic positioning
    x_offset = 100
    y_offset = 100
    spacing = 200
    
    for i, component in enumerate(components):
        pos_x = x_offset + (i % 3) * spacing
        pos_y = y_offset + (i // 3) * spacing
        
        if component.type == 'arduino':
            result = add_arduino.invoke({
                "top": pos_y, 
                "left": pos_x, 
                "component_id": component.name
            })
        elif component.type == 'led':
            result = add_led.invoke({
                "top": pos_y, 
                "left": pos_x, 
                "color": component.properties.get('color', 'red'),
                "component_id": component.name
            })
        elif component.type == 'servo':
            result = add_servo.invoke({
                "top": pos_y, 
                "left": pos_x,
                "component_id": component.name
            })
        
        results.append(result)
    
    # Add connections
    for connection in connections:
        result = add_connection.invoke({
            "from_component": connection.from_component,
            "from_pin": connection.from_pin,
            "to_component": connection.to_component,
            "to_pin": connection.to_pin,
            "color": connection.wire_color
        })
        results.append(result)
    
    return "Circuit built successfully:\n" + "\n".join(results)


@tool 
def explain_circuit() -> str:
    """Explain the current circuit configuration and functionality."""
    circuit_manager = CircuitManager.get_instance()
    
    if not circuit_manager.components:
        return "No circuit components found. Build a circuit first."
    
    components = circuit_manager.list_components()
    connections = circuit_manager.list_connections()
    
    explanation = ["Circuit Analysis:"]
    
    # Analyze components
    component_types = {}
    for comp in components:
        comp_type = comp['type']
        component_types[comp_type] = component_types.get(comp_type, 0) + 1
    
    explanation.append("\nComponents:")
    for comp_type, count in component_types.items():
        if comp_type == 'wokwi-arduino-uno':
            explanation.append(f"- {count} Arduino Uno microcontroller(s) - the main control board")
        elif comp_type == 'wokwi-led':
            explanation.append(f"- {count} LED(s) - light emitting diode(s) for visual output")
        elif comp_type == 'wokwi-servo':
            explanation.append(f"- {count} Servo motor(s) - precise rotational actuator(s)")
    
    # Analyze connections
    explanation.append(f"\nConnections: {len(connections)} wire(s) connecting the components")
    
    # Provide functionality explanation
    explanation.append("\nFunctionality:")
    if 'wokwi-arduino-uno' in component_types:
        explanation.append("- Arduino Uno serves as the main controller")
        
        if 'wokwi-led' in component_types:
            explanation.append("- LEDs can be controlled to turn on/off or blink")
            explanation.append("- LEDs are typically connected to digital pins for control")
        
        if 'wokwi-servo' in component_types:
            explanation.append("- Servo motors can be positioned at specific angles (0-180 degrees)")
            explanation.append("- Servos require PWM signals typically on pins 9, 10, or 11")
    
    return "\n".join(explanation)


# Export all tools for agent use
wokwi_tools = [
    add_arduino,
    add_led,
    add_servo, 
    add_connection,
    list_components,
    clear_circuit,
    generate_diagram,
    parse_circuit_description,
    build_circuit_from_description,
    explain_circuit
]