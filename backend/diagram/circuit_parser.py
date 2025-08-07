import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ComponentSpec:
    type: str
    name: Optional[str] = None
    properties: Dict[str, Any] = None
    pin: Optional[str] = None
    position: Optional[Tuple[float, float]] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class ConnectionSpec:
    from_component: str
    from_pin: str
    to_component: str
    to_pin: str
    wire_color: str = "green"


class CircuitParser:
    """Parse natural language circuit descriptions."""
    
    COMPONENT_PATTERNS = {
        'arduino': [
            r'arduino\s*(?:uno)?',
            r'microcontroller',
            r'board'
        ],
        'led': [
            r'led',
            r'light\s*emitting\s*diode',
            r'(?:red|green|blue|yellow|white)\s*light'
        ],
        'servo': [
            r'servo\s*motor?',
            r'servo',
            r'motor'
        ]
    }
    
    COLOR_PATTERNS = {
        'red': [r'red', r'crimson'],
        'green': [r'green', r'lime'],
        'blue': [r'blue', r'cyan'],
        'yellow': [r'yellow', r'gold'],
        'white': [r'white', r'clear']
    }
    
    PIN_PATTERNS = [
        r'pin\s*(\d+)',
        r'digital\s*pin\s*(\d+)',
        r'analog\s*pin\s*([a-z]\d+)',
        r'pin\s*([a-z]\d+)',
        r'port\s*(\w+)'
    ]
    
    def parse_components(self, description: str) -> List[ComponentSpec]:
        """Extract components from description."""
        description = description.lower()
        components = []
        
        # Find Arduino boards
        for pattern in self.COMPONENT_PATTERNS['arduino']:
            if re.search(pattern, description):
                components.append(ComponentSpec(
                    type='arduino',
                    name='arduino1',
                    properties={'type': 'uno'}
                ))
                break
        
        # Find LEDs with colors
        led_matches = []
        for pattern in self.COMPONENT_PATTERNS['led']:
            matches = re.finditer(pattern, description)
            for match in matches:
                color = self._extract_color_near_position(description, match.start())
                led_matches.append(ComponentSpec(
                    type='led',
                    name=f'led{len(led_matches) + 1}',
                    properties={'color': color or 'red'}
                ))
        components.extend(led_matches)
        
        # Find Servos
        for pattern in self.COMPONENT_PATTERNS['servo']:
            if re.search(pattern, description):
                components.append(ComponentSpec(
                    type='servo',
                    name='servo1',
                    properties={'type': 'standard'}
                ))
                break
        
        return components
    
    def parse_connections(self, description: str, components: List[ComponentSpec]) -> List[ConnectionSpec]:
        """Extract connection requirements."""
        description = description.lower()
        connections = []
        
        # Look for pin mentions
        pin_matches = []
        for pattern in self.PIN_PATTERNS:
            matches = re.finditer(pattern, description)
            for match in matches:
                pin_matches.append(match.group(1))
        
        # Create connections based on components and pins
        arduino = next((c for c in components if c.type == 'arduino'), None)
        if arduino:
            component_index = 0
            for component in components:
                if component.type == 'arduino':
                    continue
                    
                # Determine pin based on component type
                if component.type == 'led':
                    pin = pin_matches[component_index] if component_index < len(pin_matches) else '13'
                    connections.append(ConnectionSpec(
                        from_component=component.name,
                        from_pin='cathode',
                        to_component=arduino.name,
                        to_pin=pin,
                        wire_color='green'
                    ))
                    connections.append(ConnectionSpec(
                        from_component=component.name,
                        from_pin='anode',
                        to_component=arduino.name,
                        to_pin='5V',
                        wire_color='red'
                    ))
                elif component.type == 'servo':
                    pin = pin_matches[component_index] if component_index < len(pin_matches) else '9'
                    connections.extend([
                        ConnectionSpec(
                            from_component=component.name,
                            from_pin='signal',
                            to_component=arduino.name,
                            to_pin=pin,
                            wire_color='yellow'
                        ),
                        ConnectionSpec(
                            from_component=component.name,
                            from_pin='power',
                            to_component=arduino.name,
                            to_pin='5V',
                            wire_color='red'
                        ),
                        ConnectionSpec(
                            from_component=component.name,
                            from_pin='ground',
                            to_component=arduino.name,
                            to_pin='GND',
                            wire_color='black'
                        )
                    ])
                
                component_index += 1
        
        return connections
    
    def _extract_color_near_position(self, text: str, position: int) -> Optional[str]:
        """Extract color mentioned near a specific position in text."""
        # Look in a window around the position
        window_size = 20
        start = max(0, position - window_size)
        end = min(len(text), position + window_size)
        window_text = text[start:end]
        
        for color, patterns in self.COLOR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, window_text):
                    return color
        
        return None
    
    def validate_circuit(self, components: List[ComponentSpec], connections: List[ConnectionSpec]) -> Tuple[bool, List[str]]:
        """Validate circuit feasibility."""
        errors = []
        
        # Check if we have at least one Arduino
        arduino_count = sum(1 for c in components if c.type == 'arduino')
        if arduino_count == 0:
            errors.append("Circuit requires at least one Arduino microcontroller")
        
        # Check component limits
        led_count = sum(1 for c in components if c.type == 'led')
        if led_count > 13:  # Arduino Uno has 13 digital pins
            errors.append(f"Too many LEDs ({led_count}). Arduino Uno supports up to 13 digital components")
        
        servo_count = sum(1 for c in components if c.type == 'servo')
        if servo_count > 6:  # Conservative estimate for servo power requirements
            errors.append(f"Too many servos ({servo_count}). Recommended maximum is 6 for power stability")
        
        # Validate connections
        component_names = {c.name for c in components}
        for conn in connections:
            if conn.from_component not in component_names:
                errors.append(f"Connection references unknown component: {conn.from_component}")
            if conn.to_component not in component_names:
                errors.append(f"Connection references unknown component: {conn.to_component}")
        
        return len(errors) == 0, errors


class CircuitValidator:
    """Validate circuit designs for electrical correctness."""
    
    ARDUINO_PINS = {
        'digital': [str(i) for i in range(14)],
        'analog': [f'A{i}' for i in range(6)],
        'power': ['5V', '3.3V', 'VIN'],
        'ground': ['GND']
    }
    
    LED_PINS = ['anode', 'cathode']
    SERVO_PINS = ['signal', 'power', 'ground']
    
    def validate_connections(self, connections: List[ConnectionSpec]) -> Tuple[bool, List[str]]:
        """Check for electrical validity."""
        errors = []
        used_pins = {}
        
        for conn in connections:
            # Validate pin existence
            if not self._is_valid_pin(conn.from_component, conn.from_pin):
                errors.append(f"Invalid pin {conn.from_pin} on component {conn.from_component}")
            
            if not self._is_valid_pin(conn.to_component, conn.to_pin):
                errors.append(f"Invalid pin {conn.to_pin} on component {conn.to_component}")
            
            # Check for pin conflicts (multiple connections to same pin)
            to_key = f"{conn.to_component}.{conn.to_pin}"
            if to_key in used_pins and conn.to_pin not in self.ARDUINO_PINS['power'] + self.ARDUINO_PINS['ground']:
                errors.append(f"Pin conflict: {to_key} is connected to multiple components")
            used_pins[to_key] = conn.from_component
        
        return len(errors) == 0, errors
    
    def check_component_limits(self, components: List[ComponentSpec]) -> Tuple[bool, List[str]]:
        """Ensure component count is reasonable."""
        errors = []
        
        # Power consumption check
        total_current = 0
        for component in components:
            if component.type == 'led':
                total_current += 20  # ~20mA per LED
            elif component.type == 'servo':
                total_current += 100  # ~100mA per servo (conservative)
        
        if total_current > 500:  # Arduino can supply ~500mA total
            errors.append(f"Total current consumption ({total_current}mA) exceeds Arduino capacity (~500mA)")
        
        return len(errors) == 0, errors
    
    def _is_valid_pin(self, component_name: str, pin_name: str) -> bool:
        """Check if a pin exists on a component."""
        if 'arduino' in component_name.lower():
            return (pin_name in self.ARDUINO_PINS['digital'] + 
                   self.ARDUINO_PINS['analog'] + 
                   self.ARDUINO_PINS['power'] + 
                   self.ARDUINO_PINS['ground'])
        elif 'led' in component_name.lower():
            return pin_name in self.LED_PINS
        elif 'servo' in component_name.lower():
            return pin_name in self.SERVO_PINS
        
        return False