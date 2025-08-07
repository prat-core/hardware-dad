from pydantic import BaseModel
from enum import Enum
from typing import Dict, Any


class ComponentType(str, Enum):
    ARDUINO_UNO = "wokwi-arduino-uno"
    LED = "wokwi-led"
    SERVO = "wokwi-servo"


class Component(BaseModel):
    id: str
    type: ComponentType
    top: float = 0
    left: float = 0
    attrs: Dict[str, Any] = {}