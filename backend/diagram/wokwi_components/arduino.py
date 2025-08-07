from base import Component, ComponentType
from typing import Dict, Any


class ArduinoUno(Component):
    def __init__(self, component_id: str, top: float = 0, left: float = 0, attrs: Dict[str, Any] = None):
        super().__init__(
            id=component_id,
            type=ComponentType.ARDUINO_UNO,
            top=top,
            left=left,
            attrs=attrs or {}
        )