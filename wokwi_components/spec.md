# Wokwi Components MVP Specification

This document outlines the MVP specification for the wokwi_components module using wokwi-elements for Arduino and LED components only.

## 1. Technology Stack

* **Primary Framework:** [wokwi-elements](https://github.com/wokwi/wokwi-elements) - Web Components for Arduino and LED
* **Python Libraries:**
  * **Pydantic** - Data validation and serialization
  * **typing** - Type hints
  * **enum** - Component type definitions

## 2. API Endpoints

### Component Factory API
* **`create_component(component_type: str, **kwargs)`**: Creates Arduino or LED component
* **`to_wokwi_format(components, connections)`**: Converts to Wokwi diagram.json

## 3. Implementation Details

### MVP Architecture
```
wokwi_components/
├── __init__.py
├── base.py              # Base Component class
├── arduino.py           # Arduino Uno component
├── led.py              # LED component
└── serializer.py       # Wokwi format conversion
```

### Supported Components
1. **Arduino Uno** (`wokwi-arduino-uno`)
2. **LED** (`wokwi-led`)

### Base Implementation
```python
from pydantic import BaseModel
from enum import Enum

class ComponentType(str, Enum):
    ARDUINO_UNO = "wokwi-arduino-uno"
    LED = "wokwi-led"

class Component(BaseModel):
    id: str
    type: ComponentType
    top: float = 0
    left: float = 0
    attrs: dict = {}
```

## 4. Additional Notes

### MVP Scope
- Focus on Arduino Uno + LED circuits only
- Simple component creation and Wokwi serialization
- Basic validation for required properties
- Foundation for future component expansion