# Wokwi Component Tools Documentation

This document provides comprehensive documentation for the Wokwi LangChain tools used to build electronic circuits programmatically.

## Overview

The Wokwi Component Tools are a set of LangChain tools that allow you to:
- Add electronic components (Arduino, LEDs, Servos) to a circuit
- Create electrical connections between components  
- Generate Wokwi-compatible diagram.json files
- Manage circuit state across multiple operations

## Available Tools

### 1. add_arduino

**Description:** Add an Arduino Uno microcontroller to the circuit.

**Parameters:**
- `top` (float, default=0): Top position in pixels
- `left` (float, default=0): Left position in pixels  
- `component_id` (str, optional): Custom component ID (auto-generated if not provided)

**Returns:** Success message with component ID

**Example:**
```python
# Add Arduino at position (100, 100)
result = add_arduino.invoke({"top": 100, "left": 100})
# Result: "Added wokwi-arduino-uno with ID: arduino_1"

# Add Arduino with custom ID
result = add_arduino.invoke({
    "top": 50, 
    "left": 50, 
    "component_id": "main_arduino"
})
```

### 2. add_led

**Description:** Add an LED to the circuit with optional color specification.

**Parameters:**
- `top` (float, default=0): Top position in pixels
- `left` (float, default=0): Left position in pixels
- `color` (str, optional): LED color (red, green, blue, yellow, white, etc.)
- `component_id` (str, optional): Custom component ID (auto-generated if not provided)

**Returns:** Success message with component ID

**Example:**
```python
# Add red LED at position (200, 150)
result = add_led.invoke({
    "top": 200, 
    "left": 150, 
    "color": "red"
})
# Result: "Added wokwi-led with ID: led_1"

# Add LED with default color
result = add_led.invoke({"top": 300, "left": 150})
```

### 3. add_servo

**Description:** Add a servo motor to the circuit.

**Parameters:**
- `top` (float, default=0): Top position in pixels
- `left` (float, default=0): Left position in pixels
- `component_id` (str, optional): Custom component ID (auto-generated if not provided)

**Returns:** Success message with component ID

**Example:**
```python
# Add servo at position (150, 300)
result = add_servo.invoke({"top": 150, "left": 300})
# Result: "Added wokwi-servo with ID: servo_1"
```

### 4. add_connection

**Description:** Create an electrical connection between two component pins.

**Parameters:**
- `from_component` (str, required): Source component ID
- `from_pin` (str, required): Source component pin name
- `to_component` (str, required): Target component ID
- `to_pin` (str, required): Target component pin name
- `color` (str, default="green"): Connection wire color
- `wire_routing` (list, default=[]): Wire routing instructions for custom wire paths

**Returns:** Success message confirming connection

**Example:**
```python
# Connect Arduino pin 13 to LED anode
result = add_connection.invoke({
    "from_component": "arduino_1",
    "from_pin": "13",
    "to_component": "led_1",
    "to_pin": "A"
})
# Result: "Connected arduino_1:13 to led_1:A"

# Connect with custom wire color and routing
result = add_connection.invoke({
    "from_component": "led_1",
    "from_pin": "C", 
    "to_component": "arduino_1",
    "to_pin": "GND.1",
    "color": "black",
    "wire_routing": ["v0"]
})
```

### 5. list_components

**Description:** List all components and connections currently in the circuit.

**Parameters:** None

**Returns:** JSON string containing components and connections data

**Example:**
```python
result = list_components.invoke({})
# Returns detailed JSON with all components and their properties
```

### 6. clear_circuit

**Description:** Clear all components and connections from the circuit.

**Parameters:** None

**Returns:** Success message

**Example:**
```python
result = clear_circuit.invoke({})
# Result: "Circuit cleared successfully"
```

### 7. generate_diagram

**Description:** Generate a complete Wokwi diagram.json file for the current circuit.

**Parameters:** None

**Returns:** Formatted JSON string compatible with Wokwi simulator

**Example:**
```python
result = generate_diagram.invoke({})
# Returns complete Wokwi diagram JSON
```

## Common Pin Names

### Arduino Uno Pins
- Digital pins: `0`, `1`, `2`, ..., `13`
- Analog pins: `A0`, `A1`, `A2`, `A3`, `A4`, `A5`
- Power pins: `5V`, `3.3V`, `GND`, `GND.1`, `GND.2`
- Special pins: `RESET`, `IOREF`, `VIN`

### LED Pins
- `A`: Anode (positive, longer leg)
- `C`: Cathode (negative, shorter leg)

### Servo Pins
- `GND`: Ground
- `V+`: Power (usually 5V)
- `SIG`: Signal/Control pin

## Complete Circuit Examples

### Example 1: Simple LED Circuit

```python
# Clear any existing circuit
clear_circuit.invoke({})

# Add Arduino
add_arduino.invoke({"top": 100, "left": 100})

# Add red LED
add_led.invoke({"top": 200, "left": 150, "color": "red"})

# Connect Arduino pin 13 to LED anode
add_connection.invoke({
    "from_component": "arduino_1",
    "from_pin": "13",
    "to_component": "led_1", 
    "to_pin": "A"
})

# Connect LED cathode to ground
add_connection.invoke({
    "from_component": "led_1",
    "from_pin": "C",
    "to_component": "arduino_1",
    "to_pin": "GND.1"
})

# Generate final diagram
diagram = generate_diagram.invoke({})
```

### Example 2: Multi-LED Circuit

```python
# Setup circuit with Arduino and multiple LEDs
clear_circuit.invoke({})
add_arduino.invoke({"top": 100, "left": 100})

# Add multiple LEDs
add_led.invoke({"top": 200, "left": 200, "color": "red"})    # led_1
add_led.invoke({"top": 250, "left": 200, "color": "green"})  # led_2  
add_led.invoke({"top": 300, "left": 200, "color": "blue"})   # led_3

# Connect each LED to different Arduino pins
connections = [
    {"pin": "11", "led": "led_1"},
    {"pin": "12", "led": "led_2"}, 
    {"pin": "13", "led": "led_3"}
]

for conn in connections:
    # Connect Arduino pin to LED anode
    add_connection.invoke({
        "from_component": "arduino_1",
        "from_pin": conn["pin"],
        "to_component": conn["led"],
        "to_pin": "A"
    })
    
    # Connect LED cathode to ground
    add_connection.invoke({
        "from_component": conn["led"], 
        "from_pin": "C",
        "to_component": "arduino_1",
        "to_pin": "GND.1"
    })

diagram = generate_diagram.invoke({})
```

### Example 3: Servo Motor Circuit

```python
# Setup Arduino and servo
clear_circuit.invoke({})
add_arduino.invoke({"top": 100, "left": 100})
add_servo.invoke({"top": 150, "left": 300})

# Connect servo signal pin to Arduino pin 9
add_connection.invoke({
    "from_component": "arduino_1",
    "from_pin": "9", 
    "to_component": "servo_1",
    "to_pin": "SIG"
})

# Connect servo power
add_connection.invoke({
    "from_component": "arduino_1",
    "from_pin": "5V",
    "to_component": "servo_1", 
    "to_pin": "V+"
})

# Connect servo ground
add_connection.invoke({
    "from_component": "arduino_1",
    "from_pin": "GND.1",
    "to_component": "servo_1",
    "to_pin": "GND"
})

diagram = generate_diagram.invoke({})
```

## Error Handling

The tools include built-in error handling for common issues:

- **Component not found**: `"Error: Component 'component_id' not found"`
- **Duplicate component ID**: `"Error: Component with ID 'component_id' already exists"`
- **Empty circuit**: `"Error: No components in circuit. Add some components first."`

## Output Format

The `generate_diagram` tool produces JSON in the standard Wokwi format:

```json
{
  "version": 1,
  "author": "wokwi_components", 
  "editor": "wokwi",
  "parts": [
    { "type": "wokwi-arduino-uno", "id": "arduino_1", "top": 100, "left": 100, "attrs": {} }
  ],
  "connections": [
    [ "arduino_1:13", "led_1:A", "green", [] ]
  ],
  "dependencies": {}
}
```

This JSON can be directly imported into the Wokwi simulator for testing and simulation.

## Best Practices

1. **Always clear the circuit** before starting a new design
2. **Use descriptive component IDs** when needed for complex circuits
3. **Connect ground properly** - use `GND.1`, `GND.2` etc. for multiple ground connections
4. **Check component list** periodically during complex builds
5. **Generate and save diagrams** after completing circuits
6. **Use appropriate wire colors** for better circuit readability (red for power, black for ground, etc.)