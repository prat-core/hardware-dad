# Wokwi LangChain Tools

This directory contains LangChain/LangGraph tools for creating and managing Wokwi circuit diagrams programmatically using AI agents.

## Overview

The tools enable AI agents to:
- Add electronic components (Arduino, LEDs, Servos) to circuits
- Create connections between components  
- Manage circuit state across multiple tool calls
- Generate final `diagram.json` files compatible with Wokwi simulator

## Files Structure

```
tools/
├── README.md              # This file
├── spec.md               # Implementation specification
├── __init__.py           # Package initialization
├── circuit_manager.py    # Circuit state management (singleton)
├── component_tools.py    # LangChain tool definitions
├── test_tools.py        # Test script
└── example_usage.py     # Usage examples and integration guide
```

## Available Tools

### Component Tools
- `add_arduino` - Add Arduino Uno to circuit
- `add_led` - Add LED with optional color
- `add_servo` - Add servo motor

### Connection Tools  
- `add_connection` - Create wired connections between component pins

### Management Tools
- `list_components` - List all components and connections
- `clear_circuit` - Reset circuit to empty state
- `generate_diagram` - Create final Wokwi diagram.json

## Quick Start

```python
from tools import (
    add_arduino, add_led, add_connection, generate_diagram
)

# Add components
arduino_result = add_arduino.invoke({"top": 100, "left": 100})
led_result = add_led.invoke({"top": 200, "left": 150, "color": "red"})

# Create connection
connection_result = add_connection.invoke({
    "from_component": "arduino_1",
    "from_pin": "13",
    "to_component": "led_1", 
    "to_pin": "A"
})

# Generate final diagram
diagram = generate_diagram.invoke({})
print(diagram)  # JSON string ready for Wokwi
```

## LangChain Integration

```python
from langchain_core.tools import BaseTool
from typing import List

def get_wokwi_tools() -> List[BaseTool]:
    return [
        add_arduino, add_led, add_servo, add_connection,
        list_components, clear_circuit, generate_diagram
    ]

# Use with LangChain agents
tools = get_wokwi_tools()
llm_with_tools = llm.bind_tools(tools)
```

## Testing

Run the test script to verify all tools work correctly:

```bash
cd tools
python test_tools.py
```

## Example Agent Conversations

**User**: "Create a simple LED circuit with Arduino"

**Agent Actions**:
1. `add_arduino()` - Adds Arduino Uno
2. `add_led(color="red")` - Adds red LED  
3. `add_connection(from="arduino_1.13", to="led_1.A")` - Wire connection
4. `add_connection(from="led_1.C", to="arduino_1.GND")` - Ground connection
5. `generate_diagram()` - Creates final JSON

**User**: "Add a servo motor to pin 9"

**Agent Actions**:
1. `add_servo()` - Adds servo motor
2. `add_connection(from="arduino_1.9", to="servo_1.SIG")` - Signal wire
3. `add_connection(from="arduino_1.5V", to="servo_1.V+")` - Power wire
4. `add_connection(from="arduino_1.GND", to="servo_1.V-")` - Ground wire

## Circuit State Management

The `CircuitManager` class maintains circuit state as a singleton across all tool calls, ensuring:
- Component persistence between tool invocations
- Unique component ID generation
- Connection validation
- State consistency

## Output Format

Generated diagrams follow the Wokwi `diagram.json` specification:

```json
{
  "version": 1,
  "author": "wokwi_components", 
  "editor": "wokwi",
  "parts": [
    {
      "type": "wokwi-arduino-uno",
      "id": "arduino_1", 
      "top": 100,
      "left": 100,
      "attrs": {}
    }
  ],
  "connections": [
    ["arduino_1.13", "led_1.A", "green", ["v0"]]
  ],
  "dependencies": {}
}
```

## Dependencies

- `langchain-core` - Tool decorators and base classes
- `pydantic` - Input validation schemas  
- `wokwi_components` - Component classes and serialization

## Future Enhancements

- Additional component types (resistors, capacitors, sensors)
- Automatic component placement algorithms
- Circuit validation and error checking
- Arduino code generation
- Import existing diagram.json files