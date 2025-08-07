from base import Component, ComponentType
from typing import Dict, Any, Optional


class LED(Component):
    def __init__(self, component_id: str, top: float = 0, left: float = 0, 
                 color: Optional[str] = None, attrs: Dict[str, Any] = None):
        led_attrs = attrs or {}
        if color:
            led_attrs["color"] = color
            
        super().__init__(
            id=component_id,
            type=ComponentType.LED,
            top=top,
            left=left,
            attrs=led_attrs
        )