import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Bot, Send, Lightbulb, Zap, Plus, History } from "lucide-react";

interface AgentSidebarProps {
  onPromptSubmit: (prompt: string) => void;
}

const presetPrompts = [
  {
    title: "Add Blinking LED",
    prompt: "Add a red LED to pin 13 and create a simple blinking program",
    icon: <Lightbulb className="w-4 h-4" />,
    category: "Basic"
  },
  {
    title: "Temperature Sensor",
    prompt: "Connect a DHT11 temperature sensor to pin 2 and display readings on serial monitor",
    icon: <Zap className="w-4 h-4" />,
    category: "Sensors"
  },
  {
    title: "LCD Display",
    prompt: "Add a 16x2 LCD display and show 'Hello World' message",
    icon: <Plus className="w-4 h-4" />,
    category: "Display"
  },
  {
    title: "Servo Control",
    prompt: "Connect a servo motor to pin 9 and make it sweep from 0 to 180 degrees",
    icon: <Zap className="w-4 h-4" />,
    category: "Motors"
  },
];

const recentPrompts = [
  "Add a blue LED to pin 12",
  "Replace Arduino with ESP32",
  "Connect buzzer to pin 8",
  "Add ultrasonic sensor",
];

export const AgentSidebar = ({ onPromptSubmit }: AgentSidebarProps) => {
  const [prompt, setPrompt] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async () => {
    if (!prompt.trim()) return;
    
    setIsProcessing(true);
    onPromptSubmit(prompt);
    
    // Simulate AI processing
    setTimeout(() => {
      setIsProcessing(false);
      setPrompt("");
    }, 2000);
  };

  const handlePresetClick = (presetPrompt: string) => {
    setPrompt(presetPrompt);
  };

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header flex items-center gap-2">
        <Bot className="w-4 h-4 text-primary" />
        <h3 className="font-semibold">AI Hardware Agent</h3>
        <Badge variant="outline" className="ml-auto text-xs">Beta</Badge>
      </div>
      
      <div className="flex-1 flex flex-col p-4 gap-4 min-h-0">
        {/* Agent Status */}
        <div className="agent-prompt">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">Agent Active</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Describe what you want to build and I'll help you configure the hardware and code.
          </p>
        </div>

        {/* Prompt Input */}
        <div className="space-y-3">
          <Textarea
            placeholder="e.g., 'Add a red LED to pin 13 and make it blink every second'"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="min-h-[100px] resize-none"
            disabled={isProcessing}
          />
          <Button 
            onClick={handleSubmit}
            disabled={!prompt.trim() || isProcessing}
            className="w-full"
          >
            {isProcessing ? (
              <>
                <div className="w-4 h-4 mr-2 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Send Prompt
              </>
            )}
          </Button>
        </div>

        {/* Preset Prompts */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium flex items-center gap-2">
            <Lightbulb className="w-4 h-4" />
            Quick Start
          </h4>
          <ScrollArea className="h-48">
            <div className="space-y-2">
              {presetPrompts.map((preset, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="w-full justify-start text-left h-auto p-3"
                  onClick={() => handlePresetClick(preset.prompt)}
                  disabled={isProcessing}
                >
                  <div className="flex items-start gap-2">
                    <div className="text-primary mt-0.5">
                      {preset.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm">{preset.title}</div>
                      <div className="text-xs text-muted-foreground mt-1 line-clamp-2">
                        {preset.prompt}
                      </div>
                      <Badge variant="outline" className="mt-2 text-xs">
                        {preset.category}
                      </Badge>
                    </div>
                  </div>
                </Button>
              ))}
            </div>
          </ScrollArea>
        </div>

        {/* Recent Prompts */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium flex items-center gap-2">
            <History className="w-4 h-4" />
            Recent
          </h4>
          <ScrollArea className="flex-1">
            <div className="space-y-1">
              {recentPrompts.map((recentPrompt, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  className="w-full justify-start text-xs h-auto p-2 text-muted-foreground hover:text-foreground"
                  onClick={() => handlePresetClick(recentPrompt)}
                  disabled={isProcessing}
                >
                  <span className="truncate">{recentPrompt}</span>
                </Button>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>
    </div>
  );
};