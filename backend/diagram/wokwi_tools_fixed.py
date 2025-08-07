"""
Fixed Wokwi component tools for LangChain/LangGraph agent integration.
"""

from langchain_core.tools import tool
from typing import List, Optional
import json
import sys
import os

# Add the tools directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from circuit_manager import CircuitManager
from wokwi_components.arduino import ArduinoUno
from wokwi_components.led import LED
from wokwi_components.servo import Servo
from wokwi_components.serializer import to_wokwi_format
from circuit_parser import CircuitParser, CircuitValidator, ComponentSpec, ConnectionSpec


@tool
def clear_circuit() -> str:
    """Clear all components and connections from the circuit."""
    circuit_manager = CircuitManager.get_instance()
    return circuit_manager.clear_circuit()


@tool
def add_arduino(top: float = 100, left: float = 100, component_id: Optional[str] = None) -> str:
    """Add an Arduino Uno microcontroller to the circuit at specified position.
    
    Args:
        top: Top position in pixels (default: 100)
        left: Left position in pixels (default: 100)
        component_id: Optional custom component ID (auto-generated if not provided)
    """
    circuit_manager = CircuitManager.get_instance()
    
    if component_id is None:
        component_id = circuit_manager.generate_component_id("arduino")
    elif circuit_manager.component_exists(component_id):
        return f"Error: Component with ID '{component_id}' already exists"
    
    arduino = ArduinoUno(component_id=component_id, top=top, left=left)
    return circuit_manager.add_component(arduino)


@tool
def add_led(top: float = 200, left: float = 200, color: str = "red", component_id: Optional[str] = None) -> str:
    """Add an LED to the circuit at specified position with specified color.
    
    Args:
        top: Top position in pixels (default: 200)
        left: Left position in pixels (default: 200)
        color: LED color (red, green, blue, yellow, white, etc.) (default: red)
        component_id: Optional custom component ID (auto-generated if not provided)
    """
    circuit_manager = CircuitManager.get_instance()
    
    if component_id is None:
        component_id = circuit_manager.generate_component_id("led")
    elif circuit_manager.component_exists(component_id):
        return f"Error: Component with ID '{component_id}' already exists"
    
    led = LED(component_id=component_id, top=top, left=left, color=color)
    return circuit_manager.add_component(led)


@tool
def add_servo(top: float = 300, left: float = 200, component_id: Optional[str] = None) -> str:
    """Add a servo motor to the circuit at specified position.
    
    Args:
        top: Top position in pixels (default: 300)
        left: Left position in pixels (default: 200)
        component_id: Optional custom component ID (auto-generated if not provided)
    """
    circuit_manager = CircuitManager.get_instance()
    
    if component_id is None:
        component_id = circuit_manager.generate_component_id("servo")
    elif circuit_manager.component_exists(component_id):
        return f"Error: Component with ID '{component_id}' already exists"
        
    servo = Servo(component_id=component_id, top=top, left=left)
    return circuit_manager.add_component(servo)


@tool
def add_connection(from_component: str, from_pin: str, to_component: str, 
                  to_pin: str, color: str = "green") -> str:
    """Create an electrical connection between two component pins.
    
    Args:
        from_component: Source component ID (e.g., 'arduino_1', 'led_1')
        from_pin: Source component pin name (e.g., '13', 'A', 'SIG')
        to_component: Target component ID (e.g., 'arduino_1', 'led_1')  
        to_pin: Target component pin name (e.g., 'GND.1', 'C', 'V+')
        color: Wire color (default: green)
    """
    circuit_manager = CircuitManager.get_instance()
    
    # Validate components exist
    if not circuit_manager.component_exists(from_component):
        return f"Error: Component '{from_component}' not found"
    if not circuit_manager.component_exists(to_component):
        return f"Error: Component '{to_component}' not found"
    
    return circuit_manager.add_connection(from_component, from_pin, to_component, to_pin, color, [])


@tool
def list_components() -> str:
    """List all components currently in the circuit with their details."""
    circuit_manager = CircuitManager.get_instance()
    components = circuit_manager.list_components()
    connections = circuit_manager.list_connections()
    
    result = {
        "components": components,
        "connections": connections
    }
    
    return json.dumps(result, indent=2)


@tool
def generate_diagram() -> str:
    """Generate final Wokwi diagram.json for the current circuit."""
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
            conn.get("wire_routing", [])
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
        return result
    
    return format_wokwi_json(diagram)


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


@tool
def build_circuit_from_description(description: str) -> str:
    """Automatically build a complete circuit from natural language description.
    
    Args:
        description: Natural language description of the desired circuit
                    (e.g., "Create a red LED connected to pin 13 of an Arduino")
    """
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


# Export all tools for agent use
wokwi_tools = [
    clear_circuit,
    add_arduino,
    add_led,
    add_servo, 
    add_connection,
    list_components,
    generate_diagram,
    explain_circuit,
    build_circuit_from_description
]


# Test the tools individually
if __name__ == "__main__":
    print("Testing Wokwi Tools...")
    
    # Test basic functionality
    print("1. Clearing circuit:", clear_circuit.invoke({}))
    print("2. Adding Arduino:", add_arduino.invoke({}))
    print("3. Adding LED:", add_led.invoke({}))
    print("4. Adding connection:", add_connection.invoke({
        "from_component": "arduino_1", 
        "from_pin": "13", 
        "to_component": "led_1", 
        "to_pin": "A"
    }))
    print("5. Listing components:")
    print(list_components.invoke({}))
    print("6. Explaining circuit:")
    print(explain_circuit.invoke({}))