from base import Component, ComponentType
from arduino import ArduinoUno
from led import LED
from servo import Servo
from serializer import to_wokwi_format
from typing import Union, Dict, Any


def create_component(component_type: str, **kwargs) -> Union[ArduinoUno, LED, Servo]:
    """
    Factory function to create Arduino or LED components.
    
    Args:
        component_type: Type of component ('wokwi-arduino-uno' or 'wokwi-led')
        **kwargs: Component parameters (id, top, left, attrs, etc.)
        
    Returns:
        Component instance
        
    Raises:
        ValueError: If component_type is not supported
    """
    if component_type == ComponentType.ARDUINO_UNO:
        return ArduinoUno(**kwargs)
    elif component_type == ComponentType.LED:
        return LED(**kwargs)
    elif component_type == ComponentType.SERVO:
        return Servo(**kwargs)
    else:
        raise ValueError(f"Unsupported component type: {component_type}")


__all__ = [
    "Component",
    "ComponentType", 
    "ArduinoUno",
    "LED",
    "Servo",
    "create_component",
    "to_wokwi_format"
]