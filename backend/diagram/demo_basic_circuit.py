"""
Demo script that directly uses the component tools to create a basic Arduino + LED circuit
This script demonstrates the tools without requiring an LLM API key.
"""

import os
import sys
import json

# Add current directory to path for tool imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.component_tools import (
    add_arduino, add_led, add_connection, 
    clear_circuit, generate_diagram, list_components
)


def create_arduino_led_circuit():
    """Create a basic Arduino + LED circuit using the tools directly"""
    
    print("="*60)
    print("CREATING ARDUINO + RED LED CIRCUIT")
    print("="*60)
    
    # Step 1: Clear any existing circuit
    print("\n1. Clearing circuit...")
    clear_result = clear_circuit.invoke({})
    print(f"   Result: {clear_result}")
    
    # Step 2: Add Arduino Uno at position (100, 100)
    print("\n2. Adding Arduino Uno...")
    arduino_result = add_arduino.invoke({
        "top": 100,
        "left": 100,
        "component_id": "main_arduino"
    })
    print(f"   Result: {arduino_result}")
    
    # Step 3: Add red LED at position (200, 200)
    print("\n3. Adding red LED...")
    led_result = add_led.invoke({
        "top": 200,
        "left": 200,
        "color": "red",
        "component_id": "status_led"
    })
    print(f"   Result: {led_result}")
    
    # Step 4: Connect Arduino pin 13 to LED anode (positive)
    print("\n4. Connecting Arduino pin 13 to LED anode...")
    connection1_result = add_connection.invoke({
        "from_component": "main_arduino",
        "from_pin": "13",
        "to_component": "status_led",
        "to_pin": "A",
        "color": "red"
    })
    print(f"   Result: {connection1_result}")
    
    # Step 5: Connect LED cathode to Arduino ground
    print("\n5. Connecting LED cathode to Arduino ground...")
    connection2_result = add_connection.invoke({
        "from_component": "status_led",
        "from_pin": "C", 
        "to_component": "main_arduino",
        "to_pin": "GND.1",
        "color": "black"
    })
    print(f"   Result: {connection2_result}")
    
    # Step 6: List current components
    print("\n6. Listing circuit components...")
    components_result = list_components.invoke({})
    print(f"   Current circuit state:\n{components_result}")
    
    # Step 7: Generate final diagram.json
    print("\n7. Generating Wokwi diagram.json...")
    diagram_result = generate_diagram.invoke({})
    print(f"   Generated diagram:")
    print(diagram_result)
    
    return diagram_result


def save_diagram_to_file(diagram_json: str, filename: str = "arduino_led_circuit.json"):
    """Save the generated diagram to a file"""
    try:
        # Parse and re-format the JSON to ensure it's valid
        diagram_data = json.loads(diagram_json)
        
        with open(filename, 'w') as f:
            json.dump(diagram_data, f, indent=2)
        
        print(f"\n✅ Diagram saved to: {filename}")
        print(f"   You can import this file into Wokwi simulator!")
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Error parsing diagram JSON: {e}")
        # Save as text file instead
        txt_filename = filename.replace('.json', '.txt')
        with open(txt_filename, 'w') as f:
            f.write(diagram_json)
        print(f"   Saved raw output to: {txt_filename}")


def main():
    """Main function to demonstrate the circuit creation"""
    print("🔧 Hardware Dad - Basic Circuit Demo")
    print("This demo creates an Arduino + LED circuit using Wokwi component tools\n")
    
    try:
        # Create the circuit
        diagram = create_arduino_led_circuit()
        
        # Save to file
        save_diagram_to_file(diagram)
        
        print("\n" + "="*60)
        print("✅ CIRCUIT CREATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nWhat was created:")
        print("• Arduino Uno microcontroller")
        print("• Red LED")  
        print("• Connection from Arduino pin 13 to LED anode")
        print("• Connection from LED cathode to Arduino ground")
        print("\nThe generated diagram.json can be imported into Wokwi for simulation!")
        
    except Exception as e:
        print(f"\n❌ Error creating circuit: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()