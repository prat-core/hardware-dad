from typing import List, Dict, Any, Union
from base import Component


def to_wokwi_format(components: List[Component], connections: List[Union[List, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Convert components and connections to Wokwi diagram.json format.
    
    Args:
        components: List of Component instances
        connections: List of connections in either array format [from, to, color, routing] 
                    or dict format {"from": str, "to": str} (will be converted)
        
    Returns:
        Dictionary in Wokwi diagram.json format
    """
    wokwi_parts = []
    
    for component in components:
        part = {
            "type": component.type.value,
            "id": component.id,
            "top": int(component.top),
            "left": int(component.left),
            "attrs": component.attrs
        }
        wokwi_parts.append(part)
    
    # Convert connections to proper Wokwi format
    wokwi_connections = []
    if connections:
        for conn in connections:
            if isinstance(conn, dict):
                # Convert dict format to array format
                wokwi_connections.append([
                    conn["from"],
                    conn["to"], 
                    "green",
                    ["v0"]
                ])
            else:
                # Already in array format
                wokwi_connections.append(conn)
    
    diagram = {
        "version": 1,
        "author": "wokwi_components",
        "editor": "wokwi",
        "parts": wokwi_parts,
        "connections": wokwi_connections,
        "dependencies": {}
    }
    
    return diagram