"""
Enhanced Anthropic LangChain Agent for Wokwi Circuit Building - Visual CLI Version
Interactive CLI interface with beautiful visual output for tool calls and thinking
"""

import os
import sys
import json
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
from colorama import Fore, Style, Back, init
from datetime import datetime

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Add current directory to path for tool imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import LLMResult

# Import the component tools
from tools.component_tools import (
    add_arduino, add_led, add_connection, 
    clear_circuit, generate_diagram, list_components, add_servo
)

# Load environment variables
load_dotenv()


class VisualCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for beautiful visual output"""
    
    def __init__(self):
        super().__init__()
        self.step_count = 0
        self.current_thought = ""
        self.tool_calls = []
        self.start_time = None
        
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Called when chain starts"""
        self.start_time = time.time()
        self.print_header("🧠 AGENT THINKING", Fore.CYAN)
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts"""
        print(f"{Fore.BLUE}💭 Processing request...{Style.RESET_ALL}")
        self.print_spinner_start()
        
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Called when LLM ends"""
        self.print_spinner_end()
        
        # Extract and display the LLM's response/thinking
        if response and response.generations:
            for generation in response.generations:
                if generation and len(generation) > 0:
                    message = generation[0].message
                    if hasattr(message, 'content') and message.content:
                        # Check if this is a text response (not a tool call)
                        if isinstance(message.content, str) and message.content.strip():
                            self.print_llm_thinking(message.content)
                        elif isinstance(message.content, list):
                            # Handle structured content
                            for item in message.content:
                                if isinstance(item, dict) and item.get('type') == 'text':
                                    text = item.get('text', '').strip()
                                    if text and not text.startswith('{'):  # Avoid JSON-like content
                                        self.print_llm_thinking(text)
        
    def on_agent_action(self, action: AgentAction, **kwargs) -> Any:
        """Called when agent takes an action"""
        self.step_count += 1
        
        # Print step header
        print(f"\n{Fore.YELLOW}📍 Step {self.step_count}: {self.format_tool_name(action.tool)}{Style.RESET_ALL}")
        
        # Show thinking process if available
        if action.log:
            # Check if log contains reasoning text
            if isinstance(action.log, str) and not action.log.startswith('{'):
                thought = self.extract_thought(action.log)
                if thought:
                    self.print_thought(thought)
        
        # Show tool call details
        self.print_tool_call(action.tool, action.tool_input)
        
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when tool starts"""
        print(f"{Fore.GREEN}  ⚙️  Executing...{Style.RESET_ALL}", end="")
        
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when tool ends"""
        print(f"\r{Fore.GREEN}  ✅ Complete!{Style.RESET_ALL}    ")
        self.print_tool_result(output)
        
    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> None:
        """Called when agent finishes"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.print_header(f"✨ TASK COMPLETED ({elapsed:.1f}s)", Fore.GREEN)
        
        if finish.return_values.get('output'):
            output = finish.return_values['output']
            # Extract text from structured output if needed
            if isinstance(output, list) and len(output) > 0:
                if isinstance(output[0], dict) and 'text' in output[0]:
                    output = output[0]['text']
            self.print_final_output(output)
    
    def print_header(self, text: str, color=Fore.CYAN):
        """Print a beautiful header"""
        width = 70
        print(f"\n{color}{'━' * width}")
        print(f"{color}  {text.center(width-4)}")
        print(f"{color}{'━' * width}{Style.RESET_ALL}")
    
    def print_thought(self, thought: str):
        """Print agent's thinking process"""
        print(f"{Fore.MAGENTA}  💡 Reasoning: {Style.DIM}{thought}{Style.RESET_ALL}")
    
    def print_llm_thinking(self, content: str):
        """Print the LLM's initial response/thinking"""
        # Clean up the content
        content = content.strip()
        if not content:
            return
            
        print(f"\n{Fore.MAGENTA}  🤔 Agent Response:{Style.RESET_ALL}")
        
        # Split into lines and format
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                # Wrap long lines
                import textwrap
                wrapped = textwrap.wrap(line, width=65, initial_indent="     ", subsequent_indent="     ")
                for wrapped_line in wrapped:
                    print(f"{Fore.WHITE}{Style.DIM}{wrapped_line}{Style.RESET_ALL}")
        print()  # Add spacing after
    
    def print_tool_call(self, tool_name: str, args: dict):
        """Print formatted tool call with visual styling"""
        print(f"{Fore.CYAN}  ╭─ Tool: {Style.BRIGHT}{tool_name}{Style.RESET_ALL}")
        
        if args:
            # Format arguments nicely
            for key, value in args.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, (list, dict)):
                    value_str = json.dumps(value, indent=4)
                    lines = value_str.split('\n')
                    print(f"{Fore.CYAN}  │  {formatted_key}: {Fore.WHITE}{lines[0]}")
                    for line in lines[1:]:
                        print(f"{Fore.CYAN}  │    {Fore.WHITE}{line}")
                else:
                    print(f"{Fore.CYAN}  │  {formatted_key}: {Fore.WHITE}{value}")
        print(f"{Fore.CYAN}  ╰──────────────────────────────{Style.RESET_ALL}")
    
    def print_tool_result(self, result: str):
        """Print tool result with formatting"""
        # Parse result for special formatting
        if "Added" in result and "with ID:" in result:
            # Component addition result
            parts = result.split("with ID:")
            component_type = parts[0].replace("Added", "").strip()
            component_id = parts[1].strip() if len(parts) > 1 else ""
            
            print(f"{Fore.GREEN}  📦 Added Component:{Style.RESET_ALL}")
            print(f"     Type: {Fore.YELLOW}{component_type}{Style.RESET_ALL}")
            print(f"     ID: {Fore.BLUE}{component_id}{Style.RESET_ALL}")
            
        elif "Connected" in result:
            # Connection result
            match = re.search(r"Connected (\S+):(\S+) to (\S+):(\S+)", result)
            if match:
                print(f"{Fore.GREEN}  🔌 Created Connection:{Style.RESET_ALL}")
                print(f"     From: {Fore.YELLOW}{match.group(1)}{Style.RESET_ALL} pin {Fore.BLUE}{match.group(2)}{Style.RESET_ALL}")
                print(f"     To: {Fore.YELLOW}{match.group(3)}{Style.RESET_ALL} pin {Fore.BLUE}{match.group(4)}{Style.RESET_ALL}")
        elif "Circuit cleared" in result:
            print(f"{Fore.YELLOW}  🗑️  Circuit cleared successfully{Style.RESET_ALL}")
        elif result.startswith("{") and "version" in result:
            # Diagram JSON result
            self.print_diagram_result(result)
        else:
            # Default result display
            print(f"{Fore.GREEN}  → {result}{Style.RESET_ALL}")
    
    def print_diagram_result(self, json_str: str):
        """Print diagram.json result with visual representation"""
        try:
            data = json.loads(json_str) if isinstance(json_str, str) else json_str
            
            print(f"{Fore.GREEN}  📄 Generated Wokwi Diagram:{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}  ╭─ Circuit Summary ─────────────────────────╮{Style.RESET_ALL}")
            
            # Count components by type
            component_counts = {}
            for part in data.get('parts', []):
                comp_type = part['type'].replace('wokwi-', '')
                component_counts[comp_type] = component_counts.get(comp_type, 0) + 1
            
            for comp_type, count in component_counts.items():
                icon = self.get_component_icon(comp_type)
                print(f"{Fore.CYAN}  │ {icon} {comp_type.title()}: {Fore.WHITE}{count}{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}  │ 🔌 Connections: {Fore.WHITE}{len(data.get('connections', []))}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  ╰───────────────────────────────────────────╯{Style.RESET_ALL}")
            
            # Show ASCII art representation
            self.print_ascii_circuit(data)
            
            print(f"\n{Fore.GREEN}  ✅ Diagram saved to: {Fore.YELLOW}diagram.json{Style.RESET_ALL}")
            
        except:
            # Fallback to simple display
            print(f"{Fore.GREEN}  → Diagram generated successfully{Style.RESET_ALL}")
    
    def print_ascii_circuit(self, data: dict):
        """Print a simple ASCII art representation of the circuit"""
        print(f"\n{Fore.BLUE}  Circuit Layout:{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}  ┌────────────────────────────────────────┐")
        
        # Find Arduino and LEDs
        arduino = None
        leds = []
        servos = []
        
        for part in data.get('parts', []):
            if 'arduino' in part['type']:
                arduino = part
            elif 'led' in part['type']:
                leds.append(part)
            elif 'servo' in part['type']:
                servos.append(part)
        
        if arduino:
            print(f"{Fore.LIGHTBLACK_EX}  │  {Fore.CYAN}╔═══════════╗{Fore.LIGHTBLACK_EX}                       │")
            print(f"{Fore.LIGHTBLACK_EX}  │  {Fore.CYAN}║  ARDUINO  ║{Fore.LIGHTBLACK_EX}                       │")
            print(f"{Fore.LIGHTBLACK_EX}  │  {Fore.CYAN}║    UNO    ║{Fore.LIGHTBLACK_EX}                       │")
            print(f"{Fore.LIGHTBLACK_EX}  │  {Fore.CYAN}╚═══════════╝{Fore.LIGHTBLACK_EX}                       │")
            
            if leds:
                print(f"{Fore.LIGHTBLACK_EX}  │       │                                │")
                for i, led in enumerate(leds):
                    color = led.get('attrs', {}).get('color', 'red')
                    led_color = self.get_led_color(color)
                    print(f"{Fore.LIGHTBLACK_EX}  │       ├────── {led_color}●{Fore.LIGHTBLACK_EX} LED_{i+1}                 │")
            
            if servos:
                for i, servo in enumerate(servos):
                    print(f"{Fore.LIGHTBLACK_EX}  │       ├────── {Fore.YELLOW}⚙{Fore.LIGHTBLACK_EX} SERVO_{i+1}              │")
        
        print(f"{Fore.LIGHTBLACK_EX}  └────────────────────────────────────────┘{Style.RESET_ALL}")
    
    def get_component_icon(self, comp_type: str) -> str:
        """Get icon for component type"""
        icons = {
            'arduino-uno': '🎛️',
            'led': '💡',
            'servo': '⚙️',
            'button': '🔘',
            'resistor': '📍',
        }
        return icons.get(comp_type, '📦')
    
    def get_led_color(self, color: str):
        """Get colored representation for LED"""
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'blue': Fore.BLUE,
            'yellow': Fore.YELLOW,
            'white': Fore.WHITE,
        }
        return colors.get(color.lower(), Fore.WHITE)
    
    def format_tool_name(self, tool_name: str) -> str:
        """Format tool name for display"""
        return tool_name.replace('_', ' ').title()
    
    def extract_thought(self, log: str) -> str:
        """Extract thinking from agent log"""
        # Look for reasoning patterns in the log
        if "need to" in log.lower():
            return log.split("need to")[1].split(".")[0].strip()
        elif "will" in log.lower():
            return log.split("will")[1].split(".")[0].strip()
        elif "should" in log.lower():
            return log.split("should")[1].split(".")[0].strip()
        return ""
    
    def print_spinner_start(self):
        """Start a loading spinner effect"""
        # Simple loading indicator
        pass
    
    def print_spinner_end(self):
        """End the loading spinner"""
        pass
    
    def print_final_output(self, output: str):
        """Print the final output with formatting"""
        print(f"\n{Fore.GREEN}  📋 Summary:{Style.RESET_ALL}")
        
        # Handle different output types
        if isinstance(output, list):
            # Extract text from list of dicts if needed
            if len(output) > 0 and isinstance(output[0], dict) and 'text' in output[0]:
                output = output[0]['text']
            else:
                output = str(output)
        elif not isinstance(output, str):
            output = str(output)
        
        # Format markdown-style text
        lines = output.split('\n')
        for line in lines:
            # Handle markdown headers
            if line.startswith('**') and line.endswith('**'):
                content = line.strip('*').strip()
                # Don't add colon if it already ends with one
                suffix = "" if content.endswith(':') else ":"
                print(f"\n  {Fore.YELLOW}{Style.BRIGHT}{content}{suffix}{Style.RESET_ALL}")
            elif line.startswith('- '):
                # Handle bullet points
                content = line[2:].strip()
                print(f"    {Fore.CYAN}•{Style.RESET_ALL} {content}")
            elif line.strip():
                # Regular text with word wrapping
                import textwrap
                wrapped = textwrap.wrap(line, width=60, initial_indent="    ", subsequent_indent="    ")
                for wrapped_line in wrapped:
                    print(wrapped_line)
            else:
                # Empty line
                print()


class EnhancedWokwiAgent:
    """Enhanced agent with beautiful visual output for circuit building"""
    
    def __init__(self):
        """Initialize the enhanced Wokwi agent"""
        
        # Initialize Anthropic Claude model
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.7,
            anthropic_api_key=api_key
        )
        
        # Define available tools
        self.tools = [
            clear_circuit,
            add_arduino,
            add_led,
            add_servo,
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
        
        # Create visual callback handler
        self.callback_handler = VisualCallbackHandler()
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,  # Disable default verbose output
            handle_parsing_errors=True,
            callbacks=[self.callback_handler]
        )
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent"""
        return """You are an expert electronics engineer specializing in Arduino circuits using Wokwi simulator.

Your task is to build electronic circuits using the provided tools. You have access to these tools:

1. clear_circuit() - Clear all components from the circuit
2. add_arduino(top, left, component_id) - Add an Arduino Uno board
3. add_led(top, left, color, component_id) - Add an LED with specified color
4. add_servo(top, left, component_id) - Add a servo motor
5. add_connection(from_component, from_pin, to_component, to_pin, color) - Connect components
6. generate_diagram() - Generate the final Wokwi diagram.json
7. list_components() - List current components in the circuit

IMPORTANT WORKFLOW:
1. Always start by clearing the circuit
2. Add components with appropriate positioning (spread them out for clarity)
3. Make all necessary electrical connections
4. Generate the final diagram

POSITIONING GUIDELINES:
- Arduino: Usually at (100, 100) as the main board
- LEDs: Position above Arduino around (50-150, 0-50) with spacing of 50-60 pixels between them
- Servos: Position to the side around (150-250, 200-300)

PIN REFERENCE:
Arduino Pins: Digital pins "0"-"13", Analog pins "A0"-"A5", Power "5V", Ground "GND.1" - "GND.3"
LED Pins: "A" (anode/positive), "C" (cathode/negative)
Servo Pins: "GND" (ground), "V+" (power), "SIG" (signal)

When creating circuits, ensure proper electrical connections and use appropriate wire colors (red for power, black for ground, other colors for signals).

IMPORTANT: Before starting to build, briefly explain your approach and what you'll be creating. Think step by step about what components are needed and how they should be connected."""

    def create_arduino_led_circuit(self) -> str:
        """Create a basic Arduino + LED circuit and return the diagram.json"""
        
        task = """Create a basic circuit with:
1. An Arduino Uno board at position (100, 100)
2. A red LED at position (90, 0)  
3. Connect Arduino pin 13 to LED anode
4. Connect LED cathode to Arduino ground
5. Generate and return the diagram.json"""

        try:
            result = self.agent_executor.invoke({"input": task})
            return result
        except Exception as e:
            return f"Error creating circuit: {str(e)}"
    
    def run_custom_task(self, task: str) -> str:
        """Run a custom circuit building task with visual output"""
        try:
            result = self.agent_executor.invoke({"input": task})
            return result
        except Exception as e:
            return f"Error executing task: {str(e)}"


def print_welcome_banner():
    """Print an enhanced welcome banner"""
    width = 70
    print(f"\n{Fore.CYAN}{'═' * width}")
    print(f"{Fore.CYAN}║{' ' * 68}║")
    print(f"{Fore.CYAN}║{Fore.YELLOW}{'🔧 HARDWARE DAD - WOKWI CIRCUIT BUILDER 🔧'.center(68)}{Fore.CYAN}║")
    print(f"{Fore.CYAN}║{Fore.WHITE}{'AI-Powered Arduino Circuit Design'.center(68)}{Fore.CYAN}║")
    print(f"{Fore.CYAN}║{' ' * 68}║")
    print(f"{Fore.CYAN}{'═' * width}{Style.RESET_ALL}")
    
    # Show fun ASCII art
    print(f"{Fore.BLUE}")
    print("         ╔═══════════╗")
    print("         ║  ARDUINO  ║")
    print("         ║    UNO    ║")
    print("         ╚═══╤═══╤═══╝")
    print("             │   │")
    print(f"           {Fore.RED}●{Fore.BLUE}─┘   └─{Fore.GREEN}●{Style.RESET_ALL}")
    print(f"         {Fore.RED}LED1{Fore.BLUE}      {Fore.GREEN}LED2{Style.RESET_ALL}")
    print()


def print_help():
    """Print enhanced help information"""
    print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║                    📚 HELP & GUIDE 📚                     ║")
    print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}🎯 How to Use:{Style.RESET_ALL}")
    print(f"  Describe your circuit in natural language and the AI will")
    print(f"  build it step by step, showing you each action it takes.")
    
    print(f"\n{Fore.YELLOW}💡 Example Requests:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}• 'Create a basic LED circuit with Arduino'")
    print(f"  {Fore.GREEN}• 'Build a traffic light with red, yellow, and green LEDs'")
    print(f"  {Fore.GREEN}• 'Add a servo motor connected to pin 9'")
    print(f"  {Fore.GREEN}• 'Make a circuit with 3 LEDs that blink in sequence'{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}🔧 Available Components:{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}• Arduino Uno microcontroller")
    print(f"  {Fore.WHITE}• LEDs (red, green, blue, yellow, white)")
    print(f"  {Fore.WHITE}• Servo motors")
    print(f"  {Fore.WHITE}• Wires and connections{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}⌨️  Commands:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}• 'demo' - Run a demonstration circuit")
    print(f"  {Fore.GREEN}• 'help' - Show this help message")
    print(f"  {Fore.GREEN}• 'clear' - Clear the screen")
    print(f"  {Fore.GREEN}• 'quit' - Exit the program{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}📤 Output:{Style.RESET_ALL}")
    print(f"  The generated circuit is saved to {Fore.YELLOW}diagram.json{Style.RESET_ALL}")
    print(f"  Import this file into Wokwi.com to simulate your circuit!")


def interactive_cli():
    """Enhanced interactive CLI interface"""
    print_welcome_banner()
    
    try:
        print(f"{Fore.YELLOW}⚡ Initializing AI Agent...{Style.RESET_ALL}", end="")
        agent = EnhancedWokwiAgent()
        print(f"\r{Fore.GREEN}✅ AI Agent Ready!                    {Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\r{Fore.RED}❌ Failed to initialize: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Tip: Set your ANTHROPIC_API_KEY environment variable{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.WHITE}Type {Fore.GREEN}'help'{Fore.WHITE} for guidance or start describing your circuit!")
    print(f"{Fore.LIGHTBLACK_EX}─────────────────────────────────────────────────────────────{Style.RESET_ALL}")
    
    while True:
        try:
            # Fancy prompt
            print()
            user_input = input(f"{Fore.YELLOW}⚡ {Fore.CYAN}Circuit Request{Fore.WHITE} → {Style.RESET_ALL}").strip()
            
            if not user_input:
                continue
                
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Fore.CYAN}👋 Thanks for using Hardware Dad!{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}Your circuits are waiting in the digital realm...{Style.RESET_ALL}\n")
                break
                
            elif user_input.lower() == 'help':
                print_help()
                continue
                
            elif user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                print_welcome_banner()
                continue
                
            elif user_input.lower() == 'demo':
                print(f"\n{Fore.MAGENTA}🎮 Running Demo Circuit...{Style.RESET_ALL}")
                result = agent.create_arduino_led_circuit()
                
            else:
                # Process custom request
                result = agent.run_custom_task(user_input)
            
            # Add spacing after completion
            print(f"\n{Fore.LIGHTBLACK_EX}─────────────────────────────────────────────────────────────{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⚠️  Interrupted{Style.RESET_ALL}")
            print(f"{Fore.CYAN}👋 See you next time!{Style.RESET_ALL}\n")
            break
            
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Try rephrasing your request{Style.RESET_ALL}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        # Demo mode
        print_welcome_banner()
        print(f"{Fore.MAGENTA}🎮 Demo Mode - Creating Arduino + LED Circuit{Style.RESET_ALL}\n")
        agent = EnhancedWokwiAgent()
        result = agent.create_arduino_led_circuit()
        print(f"\n{Fore.GREEN}✨ Demo completed!{Style.RESET_ALL}")
    else:
        # Interactive mode
        interactive_cli()


if __name__ == "__main__":
    main()