"""
Wokwi Circuit Building Agent using LangGraph and Claude.
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph.message import add_messages

from agent_state import WokwiAgentState
from wokwi_tools_fixed import wokwi_tools

# Load environment variables
load_dotenv()


class WokwiCircuitAgent:
    """Main agent for building Wokwi circuits from natural language descriptions."""
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.7):
        """Initialize the Wokwi circuit building agent."""
        
        # Initialize Claude model
        self.model = ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens=4000,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Create system prompt
        self.system_prompt = self._create_system_prompt()
        
        # Initialize memory for conversation persistence
        self.memory = InMemorySaver()
        
        # Create ReAct agent with tools and memory
        self.agent = create_react_agent(
            model=self.model,
            tools=wokwi_tools,
            prompt=self._dynamic_prompt,
            state_schema=WokwiAgentState,
            checkpointer=self.memory
        )
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        return """You are an expert electronics engineer and Wokwi circuit designer. Your role is to help users build electronic circuits by understanding their natural language descriptions and converting them into working Wokwi circuit diagrams using the available tools.

IMPORTANT: You MUST use the provided tools to actually build circuits. Do not just describe what a circuit would look like - use the tools to create it!

## MANDATORY WORKFLOW FOR CIRCUIT REQUESTS:

1. **ALWAYS start by clearing the circuit**: Use `clear_circuit` tool
2. **Add components one by one**: Use `add_arduino`, `add_led`, `add_servo` tools
3. **Create all necessary connections**: Use `add_connection` tool for each wire
4. **Generate the final diagram**: Use `generate_diagram` tool
5. **Explain the circuit**: Use `explain_circuit` tool for educational value

## AVAILABLE TOOLS AND USAGE:

### Component Tools:
- `add_arduino(top, left, component_id)`: Add Arduino Uno microcontroller
- `add_led(top, left, color, component_id)`: Add LED with specified color
- `add_servo(top, left, component_id)`: Add servo motor

### Connection Tools:
- `add_connection(from_component, from_pin, to_component, to_pin, color)`: Wire components together

### Management Tools:
- `clear_circuit()`: Clear all components (ALWAYS use first)
- `list_components()`: Show current circuit state
- `generate_diagram()`: Export Wokwi JSON (ALWAYS use at end)
- `explain_circuit()`: Provide circuit explanation

### Parsing Tools:
- `parse_circuit_description(description)`: Analyze user requirements
- `build_circuit_from_description(description)`: Auto-build complete circuit

## PIN REFERENCE:

**Arduino Uno Pins:**
- Digital: "0", "1", "2"..."13" 
- Analog: "A0", "A1"..."A5"
- Power: "5V", "3.3V", "VIN"
- Ground: "GND", "GND.1", "GND.2"

**LED Pins:**
- "A": Anode (positive)
- "C": Cathode (negative)

**Servo Pins:**
- "SIG": Signal/Control
- "V+": Power 
- "GND": Ground

## EXAMPLE WORKFLOW:
User: "Create a red LED on pin 13"

Your response should use these tools in sequence:
1. `clear_circuit()` - Clear existing circuit
2. `add_arduino(top=100, left=100)` - Add Arduino
3. `add_led(top=200, left=200, color="red")` - Add red LED  
4. `add_connection(from_component="arduino_1", from_pin="13", to_component="led_1", to_pin="A")` - Connect pin 13 to LED anode
5. `add_connection(from_component="led_1", from_pin="C", to_component="arduino_1", to_pin="GND.1")` - Connect LED cathode to ground
6. `generate_diagram()` - Create Wokwi JSON
7. `explain_circuit()` - Explain functionality

## CRITICAL RULES:
- NEVER just describe a circuit without building it
- ALWAYS use tools to create actual circuits
- ALWAYS clear circuit first with `clear_circuit()`
- ALWAYS connect LED cathodes to ground
- ALWAYS provide power and ground for servos
- ALWAYS generate final diagram with `generate_diagram()`
- Use descriptive explanations after building

When a user requests a circuit, immediately start using the tools to build it step by step!"""

    def _dynamic_prompt(self, state: WokwiAgentState, config: RunnableConfig) -> List[BaseMessage]:
        """Generate dynamic prompt based on current state and context."""
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add circuit context if available
        if state.get("circuit_context"):
            context = state["circuit_context"]
            if context.get("components"):
                component_count = len(context["components"])
                connection_count = len(context.get("connections", []))
                context_msg = f"\nCurrent circuit has {component_count} components and {connection_count} connections."
                messages.append(SystemMessage(content=context_msg))
        
        # Add user intent context if available
        if state.get("user_intent"):
            intent_msg = f"\nUser Intent: {state['user_intent']}"
            messages.append(SystemMessage(content=intent_msg))
        
        # Add conversation messages
        messages.extend(state["messages"])
        
        return messages
    
    def invoke(self, message: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Invoke the agent with a user message."""
        if config is None:
            config = {"configurable": {"thread_id": "default"}}
        
        # Create input state
        input_state = {
            "messages": [HumanMessage(content=message)],
            "circuit_context": {},
            "user_intent": message,
            "component_count": 0
        }
        
        # Invoke the agent
        result = self.agent.invoke(input_state, config=config)
        
        return result
    
    def stream(self, message: str, config: Dict[str, Any] = None):
        """Stream the agent's response."""
        if config is None:
            config = {"configurable": {"thread_id": "default"}}
        
        # Create input state
        input_state = {
            "messages": [HumanMessage(content=message)],
            "circuit_context": {},
            "user_intent": message,
            "component_count": 0
        }
        
        # Stream the agent's response
        for chunk in self.agent.stream(input_state, config=config, stream_mode="values"):
            yield chunk
    
    def get_conversation_history(self, thread_id: str = "default") -> List[BaseMessage]:
        """Get conversation history for a specific thread."""
        config = {"configurable": {"thread_id": thread_id}}
        try:
            state = self.agent.get_state(config)
            return state.values.get("messages", [])
        except:
            return []
    
    def clear_conversation(self, thread_id: str = "default"):
        """Clear conversation history for a specific thread."""
        # Note: InMemorySaver doesn't have a direct clear method
        # In production, you might want to use a different checkpointer
        pass


class WokwiAgentManager:
    """Manager class for handling multiple agent instances and configurations."""
    
    def __init__(self):
        self.agents: Dict[str, WokwiCircuitAgent] = {}
        self.default_config = {
            "model_name": "claude-3-5-sonnet-20241022",
            "temperature": 0.1
        }
    
    def get_agent(self, agent_id: str = "default", **kwargs) -> WokwiCircuitAgent:
        """Get or create an agent instance."""
        if agent_id not in self.agents:
            config = {**self.default_config, **kwargs}
            self.agents[agent_id] = WokwiCircuitAgent(**config)
        
        return self.agents[agent_id]
    
    def create_new_session(self, session_id: str, **kwargs) -> WokwiCircuitAgent:
        """Create a new agent session with custom configuration."""
        config = {**self.default_config, **kwargs}
        agent = WokwiCircuitAgent(**config)
        self.agents[session_id] = agent
        return agent


# Global agent manager instance
agent_manager = WokwiAgentManager()


def get_default_agent() -> WokwiCircuitAgent:
    """Get the default agent instance."""
    return agent_manager.get_agent()


def create_circuit_from_description(description: str, thread_id: str = "default") -> Dict[str, Any]:
    """Convenience function to create a circuit from a description."""
    agent = get_default_agent()
    return agent.invoke(description, {"configurable": {"thread_id": thread_id}})


# Example usage and testing
if __name__ == "__main__":
    # Example circuit descriptions for testing
    test_descriptions = [
        "Create a simple LED circuit with a red LED connected to pin 13 of an Arduino",
        "Build a traffic light system with red, yellow, and green LEDs",
        "Make a servo motor controller with one servo connected to pin 9",
        "Create a circuit with 2 LEDs and 1 servo motor for a simple robot"
    ]
    
    print("Wokwi Circuit Agent initialized successfully!")
    print("Example usage:")
    print("agent = get_default_agent()")
    print("result = agent.invoke('Create a simple LED circuit')")
    
    # Uncomment to run interactive test
    # agent = get_default_agent()
    # for desc in test_descriptions:
    #     print(f"\n--- Testing: {desc} ---")
    #     result = agent.invoke(desc)
    #     print("Response:", result["messages"][-1].content if result["messages"] else "No response")