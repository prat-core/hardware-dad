# Basic Wokwi Agent

This directory contains a basic Anthropic LangChain agent for creating Arduino circuits using Wokwi component tools.

## Files Created

### 1. `basic_wokwi_agent.py`
A full LangChain agent that uses Anthropic's Claude model to understand natural language instructions and build circuits using the available tools.

**Features:**
- Uses Claude 3.5 Sonnet for natural language understanding
- Integrates with all Wokwi component tools
- Creates tool-calling agent with proper prompting
- Includes error handling and verbose execution

**Usage:**
```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your_api_key_here"

# Run the agent
python basic_wokwi_agent.py
```

### 2. `demo_basic_circuit.py`
A demonstration script that directly uses the component tools without requiring an LLM API key.

**Features:**
- Creates Arduino + LED circuit programmatically
- Shows step-by-step tool usage
- Generates and saves diagram.json file
- No API key required for testing

**Usage:**
```bash
python demo_basic_circuit.py
```

## Generated Output

The demo creates a basic circuit with:
- Arduino Uno microcontroller at position (100, 100)
- Red LED at position (200, 200)
- Connection from Arduino pin 13 to LED anode (red wire)
- Connection from LED cathode to Arduino ground (black wire)

The output is a valid Wokwi `diagram.json` file that can be imported directly into the Wokwi simulator.

## Example Output

```json
{
  "version": 1,
  "author": "wokwi_components",
  "editor": "wokwi",
  "parts": [
    {
      "type": "wokwi-arduino-uno",
      "id": "main_arduino",
      "top": 100,
      "left": 100,
      "attrs": {}
    },
    {
      "type": "wokwi-led",
      "id": "status_led",
      "top": 200,
      "left": 200,
      "attrs": {
        "color": "red"
      }
    }
  ],
  "connections": [
    ["main_arduino:13", "status_led:A", "red", []],
    ["status_led:C", "main_arduino:GND.1", "black", []]
  ],
  "dependencies": {}
}
```

## Tools Used

The agent leverages these component tools from `tools/component_tools.py`:

1. `clear_circuit()` - Clear all components
2. `add_arduino()` - Add Arduino Uno board
3. `add_led()` - Add LED with color specification
4. `add_connection()` - Create electrical connections
5. `generate_diagram()` - Export Wokwi JSON format
6. `list_components()` - Show current circuit state

## Requirements

See `requirements.txt` for dependencies:
- langchain and langchain-anthropic for LLM integration
- pydantic for data validation
- python-dotenv for environment variables

## Next Steps

This basic agent demonstrates the foundation for more complex circuit building capabilities. It can be extended to:
- Support more component types (servos, sensors, etc.)
- Handle complex multi-component circuits
- Generate Arduino code along with circuits
- Integrate with the frontend for visual circuit building