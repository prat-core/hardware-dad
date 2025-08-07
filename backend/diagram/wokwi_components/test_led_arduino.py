import sys
import os
sys.path.append(os.path.dirname(__file__))

from base import ComponentType
from arduino import ArduinoUno
from led import LED
from serializer import to_wokwi_format
import json


def test_led_arduino_connection():
    """Test creating an LED connected to Arduino on pin 11"""
    
    # Create Arduino Uno component
    arduino = ArduinoUno(
        component_id="uno1",
        top=0,
        left=0
    )
    
    # Create LED component
    led = LED(
        component_id="led1",
        top=-90,
        left=90.2,
        color="red"
    )
    
    # Define connection from Arduino pin 11 to LED anode, and LED cathode to GND
    connections = [
        {
            "from": "uno1:11",
            "to": "led1:A"
        },
        {
            "from": "led1:C", 
            "to": "uno1:GND.1"
        }
    ]
    
    # Convert to Wokwi format
    diagram = to_wokwi_format([arduino, led], connections)
    
    # Print the result
    print("Generated Wokwi diagram:")
    print(json.dumps(diagram, indent=2))
    
    # Verify the structure
    assert len(diagram["parts"]) == 2
    assert diagram["parts"][0]["type"] == "wokwi-arduino-uno"
    assert diagram["parts"][1]["type"] == "wokwi-led"
    assert len(diagram["connections"]) == 2
    assert diagram["connections"][0][0] == "uno1:11"  # from
    assert diagram["connections"][0][1] == "led1:A"   # to
    assert diagram["connections"][1][0] == "led1:C"   # from
    assert diagram["connections"][1][1] == "uno1:GND.1"  # to
    
    print("\nTest passed! LED successfully connected to Arduino pin 11")
    return diagram


if __name__ == "__main__":
    test_led_arduino_connection()