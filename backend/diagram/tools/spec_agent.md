
# Anthropic Agent with Wokwi Component Tools - Technical Specification

## 1. Overview

This specification outlines the design and implementation of an AI agent powered by Anthropic's Claude model that can build electronic circuits programmatically using Wokwi component tools. The agent will be capable of understanding natural language descriptions of electronic circuits and converting them into working Wokwi diagrams.

## 2. Tech Stack and Libraries (Python)

### Core AI Framework
- **LangChain**: v0.3.x - Framework for building LLM applications with standardized interfaces
- **LangGraph**: v0.2.x - State machine orchestration for complex agent workflows 
- **langchain-anthropic**: Latest - Anthropic Claude integration for LangChain

### Agent Components
- **langchain-core**: Core abstractions and base classes
- **langchain-community**: Community-maintained integrations
- **langgraph.prebuilt**: Pre-built agent components (create_react_agent, ToolNode)

### Wokwi Integration
- **Custom Wokwi Tools**: Located in `tools/` directory
  - `add_arduino`: Add Arduino Uno microcontrollers
  - `add_led`: Add LEDs with color specification
  - `add_servo`: Add servo motors
  - `add_connection`: Create electrical connections
  - `list_components`: List current circuit components
  - `clear_circuit`: Clear circuit state
  - `generate_diagram`: Generate Wokwi-compatible JSON

### Supporting Libraries
- **pydantic**: v2.x - Data validation and settings management
- **typing**: Type hints and annotations
- **json**: JSON serialization for Wokwi format
- **python-dotenv**: Environment variable management

### Development & Testing
- **pytest**: Unit testing framework
- **black**: Code formatting
- **mypy**: Static type checking

## 3. Implementation Details

### 3.1 Agent Architecture

The agent will be built using LangGraph's React (Reasoning + Acting) pattern with the following components:

```python
# Agent State Definition
class WokwiAgentState(AgentState):
    messages: Annotated[list, add_messages]
    circuit_context: dict  # Current circuit state
    user_intent: str  # Parsed user intention
    component_count: int  # Track component usage
```

### 3.2 Tool Integration

```python
# Tool Registration
from langchain_core.tools import tool

@tool
def create_led_circuit(color: str, pin: str, location: tuple) -> str:
    """Create an LED circuit with Arduino connection."""
    # Implementation using Wokwi tools
    pass

# Tool list for agent
wokwi_tools = [
    add_arduino,
    add_led, 
    add_servo,
    add_connection,
    list_components,
    clear_circuit,
    generate_diagram
]
```

### 3.3 Agent Implementation

```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

# Initialize Claude model
model = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0.1,  # Low temperature for consistent circuit building
    max_tokens=4000
)

# Create ReAct agent with tools
agent = create_react_agent(
    model=model,
    tools=wokwi_tools,
    state_schema=WokwiAgentState,
    checkpointer=MemorySaver()  # For conversation memory
)
```

### 3.4 Circuit Parsing Logic

```python
class CircuitParser:
    """Parse natural language circuit descriptions."""
    
    def parse_components(self, description: str) -> dict:
        """Extract components from description."""
        pass
    
    def parse_connections(self, description: str) -> list:
        """Extract connection requirements."""
        pass
    
    def validate_circuit(self, components: dict, connections: list) -> bool:
        """Validate circuit feasibility."""
        pass
```

### 3.5 Error Handling & Validation

```python
class CircuitValidator:
    """Validate circuit designs for electrical correctness."""
    
    def validate_connections(self, connections: list) -> list:
        """Check for electrical validity."""
        pass
    
    def check_component_limits(self, components: dict) -> bool:
        """Ensure component count is reasonable."""
        pass
```

## 4. ASCII Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                       │
│                   (Natural Language Input)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Anthropic Agent                          │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Claude Model  │    │   Circuit Parser │                │
│  │   (3.5 Sonnet)  │◄──►│   & Validator   │                │
│  └─────────────────┘    └─────────────────┘                │
│            │                      │                         │
│            ▼                      ▼                         │
│  ┌─────────────────────────────────────────┐                │
│  │           LangGraph ReAct               │                │
│  │    ┌─────────────┐  ┌─────────────┐    │                │
│  │    │   Thought   │  │   Action    │    │                │
│  │    │   Process   │◄─┤  Selection  │    │                │
│  │    └─────────────┘  └─────────────┘    │                │
│  └─────────────────┬───────────────────────┘                │
└────────────────────┼────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Wokwi Tools Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │add_arduino  │ │  add_led    │ │ add_servo   │           │
│  │             │ │             │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │add_connection│ │list_components│ │clear_circuit│           │
│  │             │ │             │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              generate_diagram                           │ │
│  │         (Wokwi JSON Generator)                         │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Circuit State Manager                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              In-Memory Circuit State                   │ │
│  │   - Components: {id: component_data}                   │ │
│  │   - Connections: [(from, to, properties)]             │ │
│  │   - Metadata: {author, version, editor}               │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Output Generation                        │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  Wokwi JSON     │    │   Explanation   │                │
│  │  diagram.json   │    │   & Instructions│                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## 5. Architecture Explanation

### 5.1 User Interface Layer
The topmost layer handles natural language input from users. Users can describe circuits in plain English, such as "Create an LED that blinks connected to pin 13 of an Arduino" or "Build a servo motor controller circuit."

### 5.2 Anthropic Agent Core
**Claude Model**: Utilizes Claude 3.5 Sonnet for natural language understanding and reasoning about electronic circuits. The model processes user intent and determines the appropriate sequence of actions.

**Circuit Parser & Validator**: Custom component that:
- Extracts component specifications from natural language
- Identifies connection requirements 
- Validates electrical feasibility
- Suggests corrections for invalid circuits

### 5.3 LangGraph ReAct Framework
Implements the ReAct (Reasoning + Acting) pattern:

**Thought Process**: The agent reasons about:
- What components are needed
- How they should be connected
- Whether the circuit is electrically sound
- What sequence of tool calls to make

**Action Selection**: Determines which Wokwi tools to call based on the current state and user requirements.

### 5.4 Wokwi Tools Layer
Seven specialized tools that interface with the Wokwi component system:

- **Component Tools**: `add_arduino`, `add_led`, `add_servo` for placing components
- **Connection Tool**: `add_connection` for wiring components together
- **Management Tools**: `list_components`, `clear_circuit` for state management
- **Output Tool**: `generate_diagram` for creating final Wokwi JSON

### 5.5 Circuit State Manager
Maintains the current circuit state in memory:
- Component registry with positions and properties
- Connection list with wire routing information
- Circuit metadata for Wokwi compatibility

### 5.6 Output Generation
Produces two types of output:
- **Wokwi JSON**: Ready-to-import circuit diagram for the Wokwi simulator
- **Explanation**: Human-readable description of the built circuit and usage instructions

## 6. Key Features

### 6.1 Natural Language Processing
- Parse complex circuit descriptions
- Handle ambiguous component specifications
- Suggest alternatives for unavailable components

### 6.2 Circuit Validation
- Electrical rule checking (voltage levels, current limits)
- Component compatibility validation
- Connection feasibility assessment

### 6.3 Interactive Circuit Building
- Step-by-step circuit construction
- Real-time feedback on circuit validity
- Ability to modify existing circuits

### 6.4 Educational Support
- Explain circuit functionality
- Provide component information
- Suggest learning resources

## 7. Error Handling Strategy

### 7.1 Tool-Level Errors
- Component placement conflicts
- Invalid connection attempts
- Resource limitations




This specification provides a comprehensive foundation for building a sophisticated AI agent that can translate natural language circuit descriptions into working Wokwi diagrams while maintaining electrical accuracy and educational value.

