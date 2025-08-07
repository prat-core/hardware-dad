# Wokwi Components LangChain Tools Specification

This document outlines the implementation approach for creating LangChain/LangGraph tools based on the existing `wokwi_components` module.

## Overview

The tools will enable AI agents to programmatically create Arduino circuits by adding components (Arduino Uno, LEDs, Servos) and eventually generating a `diagram.json` file compatible with Wokwi simulator.

## Architecture

```
tools/
├── __init__.py
├── spec.md (this file)
├── base_tool.py        # Base class for all wokwi tools
├── component_tools.py  # Tools for adding individual components
├── circuit_manager.py  # Manages circuit state and connections
└── diagram_tools.py    # Tools for generating final diagram.json
```

## Tool Categories

### 1. Component Addition Tools

#### `AddArduinoTool`
- **Purpose**: Add an Arduino Uno to the circuit
- **Input Schema**: `{"position": {"top": float, "left": float}, "component_id": str (optional)}`
- **Output**: Component ID and confirmation message
- **Implementation**: Uses `ArduinoUno` class from `wokwi_components.arduino`

#### `AddLEDTool`
- **Purpose**: Add an LED to the circuit
- **Input Schema**: `{"position": {"top": float, "left": float}, "color": str (optional), "component_id": str (optional)}`
- **Output**: Component ID and confirmation message
- **Implementation**: Uses `LED` class from `wokwi_components.led`

#### `AddServoTool`
- **Purpose**: Add a servo motor to the circuit
- **Input Schema**: `{"position": {"top": float, "left": float}, "component_id": str (optional)}`
- **Output**: Component ID and confirmation message
- **Implementation**: Uses `Servo` class from `wokwi_components.servo`

### 2. Connection Management Tools

#### `AddConnectionTool`
- **Purpose**: Create electrical connections between components
- **Input Schema**: `{"from_component": str, "from_pin": str, "to_component": str, "to_pin": str, "color": str (optional)}`
- **Output**: Connection confirmation
- **Implementation**: Manages connection list for circuit state

### 3. Circuit State Tools

#### `ListComponentsTool`
- **Purpose**: List all components in the current circuit
- **Input Schema**: `{}`
- **Output**: List of components with their IDs, types, and positions
- **Implementation**: Returns current circuit state

#### `ClearCircuitTool`
- **Purpose**: Clear all components and connections
- **Input Schema**: `{}`
- **Output**: Confirmation message
- **Implementation**: Resets circuit manager state

### 4. Diagram Generation Tools

#### `GenerateDiagramTool`
- **Purpose**: Generate final Wokwi diagram.json
- **Input Schema**: `{}`
- **Output**: Complete diagram.json as JSON string
- **Implementation**: Uses `serializer.to_wokwi_format()` function

## Implementation Strategy

### 1. Circuit State Management

```python
from typing import List, Dict, Any
from wokwi_components.base import Component

class CircuitManager:
    """Singleton class to manage circuit state across tool calls"""
    _instance = None
    
    def __init__(self):
        self.components: List[Component] = []
        self.connections: List[Dict[str, Any]] = []
        self.component_counter: Dict[str, int] = {}
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

### 2. Base Tool Class

```python
from langchain_core.tools import BaseTool
from typing import Type
from pydantic import BaseModel

class WokwiBaseTool(BaseTool):
    """Base class for all Wokwi component tools"""
    
    def __init__(self):
        super().__init__()
        self.circuit_manager = CircuitManager.get_instance()
    
    def _generate_component_id(self, component_type: str) -> str:
        """Generate unique component ID"""
        counter = self.circuit_manager.component_counter.get(component_type, 0)
        self.circuit_manager.component_counter[component_type] = counter + 1
        return f"{component_type}_{counter + 1}"
```

### 3. Tool Decorators Approach

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class AddArduinoInput(BaseModel):
    top: float = Field(default=0, description="Top position in pixels")
    left: float = Field(default=0, description="Left position in pixels")
    component_id: str = Field(default=None, description="Optional custom component ID")

@tool("add_arduino", args_schema=AddArduinoInput)
def add_arduino(top: float = 0, left: float = 0, component_id: str = None) -> str:
    """Add an Arduino Uno to the circuit"""
    # Implementation using CircuitManager and ArduinoUno class
```

## Usage Workflow

1. **Initialize Circuit**: Agent starts with empty circuit
2. **Add Components**: Agent uses component tools to add Arduino, LEDs, etc.
3. **Create Connections**: Agent uses connection tools to wire components
4. **Review Circuit**: Agent can list components to verify circuit
5. **Generate Diagram**: Agent uses diagram tool to create final JSON

## Example Agent Workflow

```python
# Agent conversation flow:
# 1. "Add an Arduino at position 100, 100"
#    -> Uses AddArduinoTool
# 2. "Add a red LED at position 200, 150"  
#    -> Uses AddLEDTool with color="red"
# 3. "Connect Arduino pin 13 to LED positive"
#    -> Uses AddConnectionTool
# 4. "Connect LED negative to Arduino GND"
#    -> Uses AddConnectionTool  
# 5. "Generate the circuit diagram"
#    -> Uses GenerateDiagramTool -> Returns diagram.json
```

## Error Handling

- **Invalid positions**: Validate position coordinates
- **Duplicate IDs**: Auto-generate unique IDs if not provided
- **Invalid connections**: Validate pin names and component existence
- **Empty circuit**: Handle diagram generation for empty circuits

## Future Extensions

- Support for more component types (resistors, capacitors, etc.)
- Automatic component placement algorithms
- Circuit validation tools
- Code generation for Arduino sketches
- Import existing diagram.json files

## Dependencies

- `langchain-core`: For tool decorators and base classes
- `pydantic`: For input validation schemas
- Existing `wokwi_components` module: For component classes and serialization