"""
Example usage of Wokwi LangChain tools with LangGraph workflow
"""

from typing import List
from langchain_core.tools import BaseTool

# Import our custom tools
from component_tools import (
    add_arduino, add_led, add_servo, add_connection,
    list_components, clear_circuit, generate_diagram
)


def get_wokwi_tools() -> List[BaseTool]:
    """Get all Wokwi component tools for use with LangChain agents"""
    return [
        add_arduino,
        add_led, 
        add_servo,
        add_connection,
        list_components,
        clear_circuit,
        generate_diagram
    ]


# Example LangGraph workflow setup
def create_circuit_agent():
    """
    Example function showing how to set up a LangGraph agent with Wokwi tools.
    
    This would typically be integrated with LangChain/LangGraph like:
    
    from langgraph.prebuilt import ToolExecutor
    from langchain_openai import ChatOpenAI
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4")
    
    # Get tools
    tools = get_wokwi_tools()
    
    # Create tool executor
    tool_executor = ToolExecutor(tools)
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Define agent workflow
    def agent_node(state):
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def tool_node(state):
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_calls = last_message.tool_calls
        for tool_call in tool_calls:
            tool = next((t for t in tools if t.name == tool_call["name"]), None)
            if tool:
                result = tool.invoke(tool_call["args"])
                # Handle result...
        
        return {"messages": messages}
    """
    pass


# Example conversation flow
EXAMPLE_CONVERSATIONS = [
    {
        "description": "Simple LED circuit",
        "user_input": "Create a simple circuit with an Arduino and a red LED connected to pin 13",
        "expected_steps": [
            "Use add_arduino tool",
            "Use add_led tool with color='red'", 
            "Use add_connection tool for Arduino pin 13 to LED anode",
            "Use add_connection tool for LED cathode to Arduino GND",
            "Use generate_diagram tool to create final JSON"
        ]
    },
    {
        "description": "Multi-LED circuit",
        "user_input": "Create a traffic light with red, yellow, and green LEDs on pins 11, 12, 13",
        "expected_steps": [
            "Use add_arduino tool",
            "Use add_led tool with color='red'",
            "Use add_led tool with color='yellow'", 
            "Use add_led tool with color='green'",
            "Multiple add_connection tools for wiring",
            "Use generate_diagram tool"
        ]
    },
    {
        "description": "Arduino with servo",
        "user_input": "Add an Arduino with a servo motor connected to pin 9",
        "expected_steps": [
            "Use add_arduino tool",
            "Use add_servo tool",
            "Use add_connection tool for servo signal to pin 9",
            "Use add_connection tool for servo power connections",
            "Use generate_diagram tool"
        ]
    }
]


if __name__ == "__main__":
    print("Wokwi LangChain Tools - Example Usage")
    print("=" * 50)
    
    print("Available tools:")
    tools = get_wokwi_tools()
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    print(f"\nExample conversations ({len(EXAMPLE_CONVERSATIONS)} scenarios):")
    for i, example in enumerate(EXAMPLE_CONVERSATIONS, 1):
        print(f"\n{i}. {example['description']}:")
        print(f"   User: {example['user_input']}")
        print(f"   Expected steps: {', '.join(example['expected_steps'])}")