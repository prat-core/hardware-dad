import { useState } from "react";
import { ComponentLibrary } from "@/components/hardware/ComponentLibrary";
import { CodeEditor } from "@/components/editor/CodeEditor";
import { SimulatorCanvas } from "@/components/simulator/SimulatorCanvas";
import { AgentSidebar } from "@/components/agent/AgentSidebar";
import { SerialMonitor } from "@/components/console/SerialMonitor";
import { Button } from "@/components/ui/button";
import { Cpu, Play, Square, RotateCcw } from "lucide-react";

const Index = () => {
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);
  const [serialLogs, setSerialLogs] = useState<string[]>([
    "Hardware Simulation Platform initialized",
    "Waiting for components...",
  ]);

  const handleSimulationToggle = () => {
    setIsSimulationRunning(!isSimulationRunning);
    const newLog = isSimulationRunning 
      ? "Simulation stopped" 
      : "Simulation started";
    setSerialLogs(prev => [...prev, newLog]);
  };

  const handleReset = () => {
    setIsSimulationRunning(false);
    setSerialLogs(["System reset", "Hardware Simulation Platform initialized"]);
  };

  return (
    <div className="h-screen w-full bg-background flex flex-col overflow-hidden">
      {/* Top Header */}
      <header className="h-14 bg-panel border-b border-border flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Cpu className="w-6 h-6 text-primary" />
            <h1 className="text-lg font-semibold">Hardware Simulation Platform</h1>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant={isSimulationRunning ? "destructive" : "default"}
            size="sm"
            onClick={handleSimulationToggle}
            className="flex items-center gap-2"
          >
            {isSimulationRunning ? (
              <>
                <Square className="w-4 h-4" />
                Stop
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run
              </>
            )}
          </Button>
          <Button variant="outline" size="sm" onClick={handleReset}>
            <RotateCcw className="w-4 h-4" />
          </Button>
        </div>
      </header>

      {/* Main Content Grid */}
      <div className="flex-1 grid grid-cols-12 grid-rows-12 gap-4 p-4 min-h-0">
        {/* Component Library - Left Panel */}
        <div className="col-span-3 row-span-12">
          <ComponentLibrary />
        </div>

        {/* Code Editor - Top Center */}
        <div className="col-span-6 row-span-6">
          <CodeEditor />
        </div>

        {/* Agent Sidebar - Right Panel */}
        <div className="col-span-3 row-span-8">
          <AgentSidebar onPromptSubmit={(prompt) => {
            setSerialLogs(prev => [...prev, `Agent: ${prompt}`]);
          }} />
        </div>

        {/* Visual Simulator - Bottom Center */}
        <div className="col-span-6 row-span-6">
          <SimulatorCanvas isRunning={isSimulationRunning} />
        </div>

        {/* Serial Monitor - Bottom Right */}
        <div className="col-span-3 row-span-4">
          <SerialMonitor logs={serialLogs} />
        </div>
      </div>
    </div>
  );
};

export default Index;