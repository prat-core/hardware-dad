"""
Test script for creating a simple Arduino + LED circuit
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from component_tools import (
    add_arduino, add_led, add_connection, 
    list_components, clear_circuit, generate_diagram
)


def test_arduino_led_circuit():
    """Test creating Arduino with blue LED on pin 12"""
    print("Testing Arduino + Blue LED Circuit")
    print("=" * 40)
    
    # Clear circuit first
    print("1. Clear circuit:")
    result = clear_circuit.invoke({})
    print(f"   {result}")
    
    # Add Arduino
    print("\n2. Add Arduino:")
    result = add_arduino.invoke({"top": 100, "left": 100})
    print(f"   {result}")
    
    # Add blue LED
    print("\n3. Add blue LED:")
    result = add_led.invoke({"top": 200, "left": 150, "color": "blue"})
    print(f"   {result}")
    
    # Connect Arduino pin 12 to LED anode
    print("\n4. Connect Arduino pin 12 to LED anode:")
    result = add_connection.invoke({
        "from_component": "arduino_1",
        "from_pin": "12",
        "to_component": "led_1",
        "to_pin": "A"
    })
    print(f"   {result}")
    
    # Connect LED cathode to Arduino GND
    print("\n5. Connect LED cathode to Arduino GND:")
    result = add_connection.invoke({
        "from_component": "led_1",
        "from_pin": "C",
        "to_component": "arduino_1",
        "to_pin": "GND.1"
    })
    print(f"   {result}")
    
    # List components
    print("\n6. List components:")
    result = list_components.invoke({})
    print(f"   {result}")
    
    # Generate diagram
    print("\n7. Generate diagram:")
    result = generate_diagram.invoke({})
    print(f"   Generated diagram.json:")
    print(result)


if __name__ == "__main__":
    test_arduino_led_circuit()