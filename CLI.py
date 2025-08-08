"""
Basic Anthropic LangChain Agent for Wokwi Circuit Building - CLI Version
Interactive CLI interface for building Arduino circuits with visual output
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

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


class VisualAgent:
    """Custom agent executor with visual output formatting"""
    
    def __init__(self, agent_executor):
        self.agent_executor = agent_executor
        self.step_count = 0
    
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{text.center(60)}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def print_step(self, action: str, details: str = ""):
        """Print a formatted step"""
        self.step_count += 1
        print(f"\n{Fore.YELLOW}Step {self.step_count}: {action}{Style.RESET_ALL}")
        if details:
            print(f"{Fore.WHITE}{details}{Style.RESET_ALL}")
    
    def print_tool_call(self, tool_name: str, args: dict):
        """Print formatted tool call information"""
        print(f"  {Fore.GREEN}🔧 Calling tool: {tool_name}{Style.RESET_ALL}")
        if args:
            print(f"  {Fore.BLUE}📝 Arguments: {json.dumps(args, indent=2)}{Style.RESET_ALL}")
    
    def print_result(self, result: str):
        """Print formatted result"""
        print(f"  {Fore.MAGENTA}✅ Result: {result}{Style.RESET_ALL}")
    
    def print_error(self, error: str):
        """Print formatted error"""
        print(f"  {Fore.RED}❌ Error: {error}{Style.RESET_ALL}")
    
    def invoke(self, input_dict: dict):
        """Invoke the agent with visual formatting"""
        self.step_count = 0
        self.print_header("WOKWI AGENT EXECUTION")
        print(f"{Fore.WHITE}🎯 Task: {input_dict['input']}{Style.RESET_ALL}")
        
        try:
            # Patch the agent executor to capture tool calls
            original_invoke = self.agent_executor.invoke
            
            def patched_invoke(input_data):
                # This is a simplified approach - in a real implementation,
                # you'd want to hook into the agent's step-by-step execution
                result = original_invoke(input_data)
                return result
            
            result = patched_invoke(input_dict)
            
            self.print_header("EXECUTION COMPLETED")
            if isinstance(result, dict) and 'output' in result:
                print(f"{Fore.GREEN}🎉 Final Output:{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{result['output']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}🎉 Result: {result}{Style.RESET_ALL}")
            
            return result
            
        except Exception as e:
            self.print_error(str(e))
            return {"error": str(e)}


class BasicWokwiAgent:
    """Basic agent for creating simple Arduino + LED circuits with CLI interface"""
    
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
        
        # Create visual agent wrapper
        self.visual_agent = VisualAgent(self.agent_executor)
    
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
1. An Arduino Uno board at position (100, 100)
2. A red LED at position (90, 0)  
3. Connect Arduino pin 13 to LED anode
4. Connect LED cathode to Arduino ground
5. Generate and return the diagram.json"""

        try:
            result = self.visual_agent.invoke({"input": task})
            return result
        except Exception as e:
            return f"Error creating circuit: {str(e)}"
    
    def run_custom_task(self, task: str) -> str:
        """Run a custom circuit building task with visual output"""
        try:
            result = self.visual_agent.invoke({"input": task})
            return result
        except Exception as e:
            return f"Error executing task: {str(e)}"


def interactive_cli():
    """Interactive CLI interface for the Wokwi agent"""
    print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║            🔧 WOKWI CIRCUIT BUILDER CLI 🔧              ║")
    print(f"{Fore.CYAN}║                  Interactive Mode                        ║")
    print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    try:
        print(f"\n{Fore.YELLOW}🚀 Initializing Wokwi Agent...{Style.RESET_ALL}")
        agent = BasicWokwiAgent()
        print(f"{Fore.GREEN}✅ Agent initialized successfully!{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to initialize agent: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Make sure you have set the ANTHROPIC_API_KEY environment variable{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.WHITE}Available commands:")
    print(f"  {Fore.GREEN}• Enter a circuit description (e.g., 'Create an LED circuit')")
    print(f"  {Fore.GREEN}• Type 'demo' for a basic Arduino + LED example")
    print(f"  {Fore.GREEN}• Type 'help' for more information")
    print(f"  {Fore.GREEN}• Type 'quit' to exit{Style.RESET_ALL}")
    
    while True:
        try:
            print(f"\n{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
            user_input = input(f"{Fore.YELLOW}🎯 Enter your circuit request: {Style.RESET_ALL}").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"{Fore.CYAN}👋 Thank you for using Wokwi Circuit Builder!{Style.RESET_ALL}")
                break
                
            elif user_input.lower() == 'help':
                print_help()
                continue
                
            elif user_input.lower() == 'demo':
                print(f"\n{Fore.BLUE}🎮 Running demo circuit (Arduino + LED)...{Style.RESET_ALL}")
                result = agent.create_arduino_led_circuit()
                
            else:
                print(f"\n{Fore.BLUE}🔄 Processing your request...{Style.RESET_ALL}")
                result = agent.run_custom_task(user_input)
            
            # Show completion message
            print(f"\n{Fore.GREEN}🎉 Task completed! Check the output above for details.{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  Interrupted by user{Style.RESET_ALL}")
            print(f"{Fore.CYAN}👋 Thank you for using Wokwi Circuit Builder!{Style.RESET_ALL}")
            break
            
        except Exception as e:
            print(f"{Fore.RED}❌ An error occurred: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Try rephrasing your request or type 'help' for assistance{Style.RESET_ALL}")


def print_help():
    """Print help information"""
    print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║                         HELP                            ║")
    print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}This CLI helps you build Arduino circuits for Wokwi simulator.{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Example requests:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}• 'Create a basic LED circuit with Arduino'")
    print(f"  {Fore.GREEN}• 'Add a servo motor connected to pin 9'")
    print(f"  {Fore.GREEN}• 'Build a traffic light with 3 LEDs'")
    print(f"  {Fore.GREEN}• 'Create a circuit with button and LED'{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Available components:{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}• Arduino Uno boards")
    print(f"  {Fore.WHITE}• LEDs (various colors)")
    print(f"  {Fore.WHITE}• Connections and wires{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Commands:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}• 'demo' - Run a basic Arduino + LED example")
    print(f"  {Fore.GREEN}• 'help' - Show this help message")
    print(f"  {Fore.GREEN}• 'quit' - Exit the program{Style.RESET_ALL}")


def main():
    """Main function - choose between demo and interactive mode"""
    # Check if enhanced_cli.py exists and use it
    enhanced_cli_path = os.path.join(os.path.dirname(__file__), "enhanced_cli.py")
    if os.path.exists(enhanced_cli_path):
        # Use the enhanced CLI for better visual output
        import subprocess
        subprocess.run([sys.executable, enhanced_cli_path] + sys.argv[1:])
    else:
        # Fallback to original CLI
        if len(sys.argv) > 1 and sys.argv[1] == '--demo':
            # Demo mode (original functionality)
            print("Running in demo mode...")
            agent = BasicWokwiAgent()
            result = agent.create_arduino_led_circuit()
            print(f"Demo completed: {result}")
        else:
            # Interactive CLI mode
            interactive_cli()


if __name__ == "__main__":
    main()