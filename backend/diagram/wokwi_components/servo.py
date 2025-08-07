from base import Component, ComponentType
from typing import Dict, Any, Optional


class Servo(Component):
    def __init__(self, component_id: str, top: float = 0, left: float = 0, 
                 horn: Optional[str] = None, attrs: Dict[str, Any] = None):
        servo_attrs = attrs or {}
        if horn:
            servo_attrs["horn"] = horn
            
        super().__init__(
            id=component_id,
            type=ComponentType.SERVO,
            top=top,
            left=left,
            attrs=servo_attrs
        )