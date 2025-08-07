"""
Basic Anthropic LangChain Agent for Wokwi Circuit Building
This agent initializes an Arduino board, adds a red LED, and prints the diagram.json
"""

import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Add current directory to path for tool imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Import the component tools
from tools.component_tools import (
    add_arduino, add_led, add_connection, 
    clear_circuit, generate_diagram, list_components
)

# Load environment variables
load_dotenv()


class BasicWokwiAgent:
    """Basic agent for creating simple Arduino + LED circuits"""
    
    def __init__(self):
        """Initialize the basic Wokwi agent"""
        
        # Initialize Anthropic Claude model
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.7,
            max_tokens=2000,
            anthropic_api_key=api_key
        )
        
        # Define available tools
        self.tools = [
            clear_circuit,
            add_arduino,
            add_led, 
            add_connection,
            generate_diagram,
            list_components
        ]
        
        # Create system prompt
        self.system_prompt = self._create_system_prompt()
        
        # Create the agent
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent"""
        return """You are an expert electronics engineer specializing in Arduino circuits using Wokwi simulator.

Your task is to build electronic circuits using the provided tools. You have access to these tools:

1. clear_circuit() - Clear all components from the circuit
2. add_arduino(top, left, component_id) - Add an Arduino Uno board
3. add_led(top, left, color, component_id) - Add an LED with specified color
4. add_connection(from_component, from_pin, to_component, to_pin, color) - Connect components
5. generate_diagram() - Generate the final Wokwi diagram.json
6. list_components() - List current components in the circuit

IMPORTANT WORKFLOW:
1. Always start by clearing the circuit
2. Add components with appropriate positioning
3. Make all necessary electrical connections
4. Generate the final diagram

PIN REFERENCE:
Arduino Pins: Digital pins "0"-"13", Analog pins "A0"-"A5", Power "5V", Ground "GND.1" - "GND.3"
LED Pins: "A" (anode/positive), "C" (cathode/negative)

When creating circuits, ensure proper electrical connections and use appropriate wire colors (red for power, black for ground, other colors for signals).
"""

    def create_arduino_led_circuit(self) -> str:
        """Create a basic Arduino + LED circuit and return the diagram.json"""
        
        task = """Create a basic circuit with:
# 1. An Arduino Uno board at position (100, 100)
# 2. A red LED at position (90, 0)  
# 3. Connect Arduino pin 13 to LED anode
# 4. Connect LED cathode to Arduino ground
# 5. Generate and return the diagram.json"""




# Create a basic circuit with:\n1. An Arduino Uno board at position (100, 100)\n2. A red LED at position (90, 0)\n3. Connect Arduino pin 13 to LED anode\n4. Connect LED cathode to Arduino ground\n5. Generate and return the diagram.json
#         """Create a basic circuit with:
# 1. An Arduino Uno board at position (100, 100)
# 2. A red LED at position (90, 0)  
# 3. Connect Arduino pin 13 to LED anode
# 4. Connect LED cathode to Arduino ground
# 5. Generate and return the diagram.json"""
        try:
            result = self.agent_executor.invoke({"input": task})
            return result
        except Exception as e:
            return f"Error creating circuit: {str(e)}"
    
    def run_custom_task(self, task: str) -> str:
        """Run a custom circuit building task"""
        try:
            result = self.agent_executor.invoke({"input": task})
            return result
        except Exception as e:
            return f"Error executing task: {str(e)}"


def main():
    """Main function to demonstrate the basic agent"""
    print("Initializing Basic Wokwi Agent...")
    
    # Create the agent
    agent = BasicWokwiAgent()
    
    print("\n" + "="*60)
    print("CREATING ARDUINO + RED LED CIRCUIT")
    print("="*60)
    
    # Create the basic circuit
    result = agent.create_arduino_led_circuit()
    
    print("\nAgent execution completed!")
    print(f"Result: {result}")
    
    print("\n" + "="*60)
    print("CIRCUIT CREATION FINISHED")
    print("="*60)


if __name__ == "__main__":
    main()