"""
Test script for Wokwi LangChain tools
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from component_tools import (
    add_arduino, add_led, add_servo, add_connection, 
    list_components, clear_circuit, generate_diagram
)


def test_tools():
    """Test all the Wokwi tools"""
    print("Testing Wokwi LangChain Tools")
    print("=" * 40)
    
    # Clear circuit first
    print("1. Clear circuit:")
    result = clear_circuit.invoke({})
    print(f"   {result}")
    
    # Add Arduino
    print("\n2. Add Arduino:")
    result = add_arduino.invoke({"top": 100, "left": 100})
    print(f"   {result}")
    
    # Add LED
    print("\n3. Add red LED:")
    result = add_led.invoke({"top": 200, "left": 150, "color": "red"})
    print(f"   {result}")
    
    # Add another LED
    print("\n4. Add blue LED:")
    result = add_led.invoke({"top": 300, "left": 150, "color": "blue"})
    print(f"   {result}")
    
    # Add Servo
    print("\n5. Add servo:")
    result = add_servo.invoke({"top": 150, "left": 300})
    print(f"   {result}")
    
    # List components
    print("\n6. List components:")
    result = list_components.invoke({})
    print(f"   {result}")
    
    # Add connections
    print("\n7. Add connection (Arduino pin 13 to LED1 A):")
    result = add_connection.invoke({
        "from_component": "arduino_1",
        "from_pin": "13", 
        "to_component": "led_1",
        "to_pin": "A"
    })
    print(f"   {result}")
    
    print("\n8. Add connection (LED1 C to Arduino GND):")
    result = add_connection.invoke({
        "from_component": "led_1",
        "from_pin": "C",
        "to_component": "arduino_1", 
        "to_pin": "GND"
    })
    print(f"   {result}")
    
    print("\n9. Add connection (Arduino GND.1 to LED1 C with black wire):")
    result = add_connection.invoke({
        "from_component": "arduino_1",
        "from_pin": "GND.1",
        "to_component": "led_1",
        "to_pin": "C",
        "color": "black",
        "wire_routing": ["v0"]
    })
    print(f"   {result}")
    
    # Generate diagram
    print("\n10. Generate diagram:")
    result = generate_diagram.invoke({})
    print(f"   Generated diagram.json:")
    print(result)


if __name__ == "__main__":
    test_tools()