import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ZoomIn, ZoomOut, RotateCcw, Grid3X3, Move, Zap } from "lucide-react";
import { WokwiWrapper } from "@/components/wokwi/WokwiWrapper";
import { ConnectionManager, Connection } from "@/components/wokwi/ConnectionManager";

interface DroppedComponent {
  id: string;
  name: string;
  type: string;
  x: number;
  y: number;
  rotation: number;
  pins?: Array<{
    name: string;
    x: number;
    y: number;
    type?: string;
  }>;
}

interface SimulatorCanvasProps {
  isRunning: boolean;
}

export const SimulatorCanvas = ({ isRunning }: SimulatorCanvasProps) => {
  const [components, setComponents] = useState<DroppedComponent[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [zoom, setZoom] = useState(1);
  const [gridVisible, setGridVisible] = useState(true);
  const [connectionMode, setConnectionMode] = useState(false);
  const canvasRef = useRef<HTMLDivElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    
    try {
      const componentData = JSON.parse(e.dataTransfer.getData("application/json"));
      const rect = canvasRef.current?.getBoundingClientRect();
      
      if (rect) {
        const x = (e.clientX - rect.left) / zoom;
        const y = (e.clientY - rect.top) / zoom;
        
        const newComponent: DroppedComponent = {
          id: `${componentData.id}-${Date.now()}`,
          name: componentData.name,
          type: componentData.type || componentData.id,
          x,
          y,
          rotation: 0,
        };
        
        setComponents(prev => [...prev, newComponent]);
      }
    } catch (error) {
      console.error("Failed to parse dropped component:", error);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const removeComponent = (id: string) => {
    setComponents(prev => prev.filter(comp => comp.id !== id));
  };

  const rotateComponent = (id: string) => {
    setComponents(prev => prev.map(comp => 
      comp.id === id ? { ...comp, rotation: (comp.rotation + 90) % 360 } : comp
    ));
  };

  const handleConnectionCreate = (connection: Omit<Connection, 'id'>) => {
    const newConnection: Connection = {
      ...connection,
      id: `conn-${Date.now()}`,
    };
    setConnections(prev => [...prev, newConnection]);
  };

  const handleConnectionDelete = (connectionId: string) => {
    setConnections(prev => prev.filter(conn => conn.id !== connectionId));
  };

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header flex items-center justify-between">
        <h3 className="font-semibold">Visual Simulator</h3>
        <div className="flex items-center gap-2">
          <Button
            variant={connectionMode ? "default" : "outline"}
            size="sm"
            onClick={() => setConnectionMode(!connectionMode)}
            title="Toggle connection mode"
          >
            <Zap className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setGridVisible(!gridVisible)}
          >
            <Grid3X3 className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
          >
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Badge variant="outline" className="text-xs px-2">
            {Math.round(zoom * 100)}%
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setZoom(Math.min(2, zoom + 0.1))}
          >
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setZoom(1)}
          >
            <RotateCcw className="w-4 h-4" />
          </Button>
        </div>
      </div>
      
      <div className="flex-1 relative overflow-hidden">
        <div
          ref={canvasRef}
          className={`w-full h-full relative cursor-crosshair ${
            gridVisible ? 'simulator-grid' : ''
          }`}
          style={{
            transform: `scale(${zoom})`,
            transformOrigin: 'top left',
          }}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {/* Simulation Status Indicator */}
          <div className="absolute top-4 right-4 z-10">
            <Badge 
              variant={isRunning ? "default" : "outline"}
              className={`${
                isRunning 
                  ? 'bg-accent text-accent-foreground animate-pulse' 
                  : 'bg-muted text-muted-foreground'
              }`}
            >
              {isRunning ? 'Running' : 'Stopped'}
            </Badge>
          </div>

          {/* Drop Zone Message */}
          {components.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <Move className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">Drop components here</p>
                <p className="text-sm">Drag hardware from the component library</p>
              </div>
            </div>
          )}

          {/* Connection Manager */}
          <ConnectionManager
            connections={connections}
            onConnectionCreate={handleConnectionCreate}
            onConnectionDelete={handleConnectionDelete}
          />

          {/* Rendered Components using Wokwi Elements */}
          {components.map((component) => (
            <div key={component.id} className="relative">
              <WokwiWrapper
                type={component.type}
                id={component.id}
                x={component.x}
                y={component.y}
                rotation={component.rotation}
                onPinChange={(pin, value) => {
                  console.log(`Pin ${pin} on ${component.id} changed to ${value}`);
                }}
              />
              
              {/* Component interaction overlay */}
              <div
                className="absolute bg-transparent border-2 border-primary/30 rounded-lg cursor-move group hover:border-primary/60 transition-colors"
                style={{
                  left: component.x - 40,
                  top: component.y - 30,
                  width: 80,
                  height: 60,
                  pointerEvents: connectionMode ? 'none' : 'auto',
                }}
                onClick={() => !connectionMode && rotateComponent(component.id)}
                onDoubleClick={() => !connectionMode && removeComponent(component.id)}
              >
                {/* Component label */}
                <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 bg-card px-2 py-1 rounded text-xs font-medium border border-border shadow-sm">
                  {component.name}
                </div>
                
                {/* Hover controls */}
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="bg-popover border border-border rounded px-2 py-1 text-xs whitespace-nowrap shadow-lg">
                    {connectionMode ? 'Connection mode active' : 'Click to rotate • Double-click to remove'}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Canvas Status */}
      <div className="border-t border-border px-4 py-2 bg-panel-accent">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>
            {components.length} component{components.length !== 1 ? 's' : ''} • 
            {connections.length} connection{connections.length !== 1 ? 's' : ''}
            {connectionMode && ' • Connection mode active'}
          </span>
          <span>Zoom: {Math.round(zoom * 100)}% • Grid: {gridVisible ? 'On' : 'Off'}</span>
        </div>
      </div>
    </div>
  );
};