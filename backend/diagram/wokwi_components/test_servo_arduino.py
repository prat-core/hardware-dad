import sys
import os
sys.path.append(os.path.dirname(__file__))

from base import ComponentType
from arduino import ArduinoUno
from servo import Servo
from serializer import to_wokwi_format
import json


def test_servo_arduino_connection():
    """Test creating a servo connected to Arduino on pin 9"""
    
    # Create Arduino Uno component
    arduino = ArduinoUno(
        component_id="uno1",
        top=0,
        left=0
    )
    
    # Create Servo component
    servo = Servo(
        component_id="servo1",
        top=-10,
        left=150,
        horn="single"
    )
    
    # Define connections: Servo VCC to 5V, GND to GND, signal to pin 9
    connections = [
        {
            "from": "servo1:V+",
            "to": "uno1:5V"
        },
        {
            "from": "servo1:GND", 
            "to": "uno1:GND.1"
        },
        {
            "from": "servo1:PWM",
            "to": "uno1:9"
        }
    ]
    
    # Convert to Wokwi format
    diagram = to_wokwi_format([arduino, servo], connections)
    
    # Print the result
    print("Generated Wokwi diagram:")
    print(json.dumps(diagram, indent=2))
    
    # Verify the structure
    assert len(diagram["parts"]) == 2
    assert diagram["parts"][0]["type"] == "wokwi-arduino-uno"
    assert diagram["parts"][1]["type"] == "wokwi-servo"
    assert len(diagram["connections"]) == 3
    assert diagram["connections"][0][0] == "servo1:V+"  # from
    assert diagram["connections"][0][1] == "uno1:5V"    # to
    assert diagram["connections"][1][0] == "servo1:GND" # from
    assert diagram["connections"][1][1] == "uno1:GND.1" # to
    assert diagram["connections"][2][0] == "servo1:PWM" # from
    assert diagram["connections"][2][1] == "uno1:9"     # to
    
    print("\nTest passed! Servo successfully connected to Arduino pin 9")
    return diagram


if __name__ == "__main__":
    test_servo_arduino_connection()